#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import hashlib
from datetime import datetime
from os.path import abspath, dirname, exists, getmtime, join
from urllib.parse import unquote
from uuid import uuid4

import aiofiles.os
import pytz

from thumbor.engines import BaseEngine
from thumbor.result_storages import BaseStorage, ResultStorageResult
from thumbor.utils import deprecated, logger


class Storage(BaseStorage):
    PATH_FORMAT_VERSION = "v2"

    @property
    def is_auto_webp(self):
        return (
            self.context.config.AUTO_WEBP and self.context.request.accepts_webp
        )

    async def put(self, image_bytes):
        file_abspath = self.normalize_path(self.context.request.url)
        if not self.validate_path(file_abspath):
            logger.warning(
                "[RESULT_STORAGE] unable to write outside root path: %s",
                file_abspath,
            )
            return
        temp_abspath = f"{file_abspath}.{str(uuid4()).replace('-', '')}"
        file_dir_abspath = dirname(file_abspath)
        logger.debug(
            "[RESULT_STORAGE] putting at %s (%s)",
            file_abspath,
            file_dir_abspath,
        )

        await self.ensure_dir(file_dir_abspath)
        async with aiofiles.open(temp_abspath, mode="wb") as a_file:
            await a_file.write(image_bytes)

        await aiofiles.os.rename(temp_abspath, file_abspath)

    async def get(self):
        path = self.context.request.url
        file_abspath = self.normalize_path(path)

        if not self.validate_path(file_abspath):
            logger.warning(
                "[RESULT_STORAGE] unable to read from outside root path: %s",
                file_abspath,
            )
            return None

        logger.debug("[RESULT_STORAGE] getting from %s", file_abspath)

        try:
            file_mtime = await aiofiles.os.path.getmtime(file_abspath)
        except FileNotFoundError:
            legacy_path = self.normalize_path_legacy(path)
            if await aiofiles.os.path.isfile(legacy_path):
                logger.debug(
                    "[RESULT_STORAGE] migrating image from old location at %s",
                    legacy_path,
                )
                await self.ensure_dir(dirname(file_abspath))
                await aiofiles.os.rename(legacy_path, file_abspath)
                file_mtime = await aiofiles.os.path.getmtime(file_abspath)

            else:
                logger.debug(
                    "[RESULT_STORAGE] image not found at %s", file_abspath
                )
                return None

        if self.is_expired(file_mtime):
            logger.debug("[RESULT_STORAGE] cached image has expired")
            return None

        try:
            async with aiofiles.open(file_abspath, mode="rb") as a_file:
                buffer = await a_file.read()
        except IsADirectoryError:
            logger.warning(
                "[RESULT_STORAGE] cache location is a directory: %s",
                file_abspath,
            )
            return None

        result = ResultStorageResult(
            buffer=buffer,
            metadata={
                "LastModified": datetime.fromtimestamp(file_mtime).replace(
                    tzinfo=pytz.utc
                ),
                "ContentLength": len(buffer),
                "ContentType": BaseEngine.get_mimetype(buffer),
            },
        )

        return result

    def validate_path(self, path):
        return abspath(path).startswith(
            self.context.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH
        )

    def normalize_path(self, path):
        digest = hashlib.sha1(unquote(path).encode("utf-8")).hexdigest()
        root_path = (
            self.context.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH.rstrip(
                "/"
            )
        )
        prefix = "auto_webp" if self.is_auto_webp else "default"

        return f"{root_path}/{prefix}/{digest[:2]}/{digest[2:4]}/{digest[4:]}"

    def normalize_path_legacy(self, path):
        path = unquote(path)
        path_segments = [
            self.context.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH.rstrip(
                "/"
            ),
            Storage.PATH_FORMAT_VERSION,
        ]
        if self.is_auto_webp:
            path_segments.append("webp")

        path_segments.extend([self.partition(path), path.lstrip("/")])

        normalized_path = join(*path_segments).replace("http://", "")
        return normalized_path

    def partition(self, path_raw):
        path = path_raw.lstrip("/")
        return join("".join(path[0:2]), "".join(path[2:4]))

    def is_expired(self, mtime):
        expire_in_seconds = self.context.config.get(
            "RESULT_STORAGE_EXPIRATION_SECONDS", None
        )

        if expire_in_seconds is None or expire_in_seconds == 0:
            return False

        timediff = datetime.now() - datetime.fromtimestamp(mtime)
        return timediff.total_seconds() > expire_in_seconds

    @deprecated("Use result's last_modified instead")
    def last_updated(self):
        path = self.context.request.url
        file_abspath = self.normalize_path(path)
        if not self.validate_path(file_abspath):
            logger.warning(
                "[RESULT_STORAGE] unable to read from outside root path: %s",
                file_abspath,
            )
            return True
        logger.debug("[RESULT_STORAGE] getting from %s", file_abspath)

        if not exists(file_abspath) or self._deprecated_is_expired(file_abspath):
            logger.debug(
                "[RESULT_STORAGE] image not found at %s", file_abspath
            )
            return True

        return datetime.fromtimestamp(getmtime(file_abspath)).replace(
            tzinfo=pytz.utc
        )

    def _deprecated_is_expired(self, path):
        expire_in_seconds = self.context.config.get(
            "RESULT_STORAGE_EXPIRATION_SECONDS", None
        )

        if expire_in_seconds is None or expire_in_seconds == 0:
            return False

        timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
        return timediff.total_seconds() > expire_in_seconds
