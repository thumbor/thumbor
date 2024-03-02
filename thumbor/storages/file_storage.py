#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import hashlib
from datetime import datetime
from json import dumps, loads
from os.path import dirname, splitext
from uuid import uuid4

import aiofiles.os

from thumbor import storages
from thumbor.utils import logger


class Storage(storages.BaseStorage):
    async def put(self, path, file_bytes):
        file_abspath = self.path_on_filesystem(path)
        temp_abspath = f"{file_abspath}.{str(uuid4()).replace('-', '')}"
        file_dir_abspath = dirname(file_abspath)

        logger.debug("creating tempfile for %s in %s...", path, temp_abspath)

        await self.ensure_dir(file_dir_abspath)

        async with aiofiles.open(temp_abspath, mode="wb") as a_file:
            await a_file.write(file_bytes)

        logger.debug("moving tempfile %s to %s...", temp_abspath, file_abspath)
        await aiofiles.os.rename(temp_abspath, file_abspath)

        return path

    async def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        file_abspath = self.path_on_filesystem(path)
        file_dir_abspath = dirname(file_abspath)

        await self.ensure_dir(file_dir_abspath)

        if not self.context.server.security_key:
            raise RuntimeError(
                "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be "
                "True if no SECURITY_KEY specified"
            )

        crypto_path = f"{splitext(file_abspath)[0]}.txt"
        temp_abspath = f"{crypto_path}.{str(uuid4()).replace('-', '')}"
        async with aiofiles.open(temp_abspath, mode="wb") as a_file:
            try:
                security_key = self.context.server.security_key.encode()
            except (UnicodeDecodeError, AttributeError):
                security_key = self.context.server.security_key
            await a_file.write(security_key)

        await aiofiles.os.rename(temp_abspath, crypto_path)
        logger.debug(
            "Stored crypto at %s (security key: %s)",
            crypto_path,
            self.context.server.security_key,
        )

        return file_abspath

    async def put_detector_data(self, path, data):
        file_abspath = self.path_on_filesystem(path)

        path = f"{splitext(file_abspath)[0]}.detectors.txt"
        temp_abspath = f"{path}.{str(uuid4()).replace('-', '')}"

        file_dir_abspath = dirname(file_abspath)
        await self.ensure_dir(file_dir_abspath)

        async with aiofiles.open(
            temp_abspath, mode="w", encoding="utf-8"
        ) as a_file:
            await a_file.write(dumps(data))

        await aiofiles.os.rename(temp_abspath, path)

        return file_abspath

    async def get(self, path):
        abs_path = self.path_on_filesystem(path)

        resource_available = await self.exists(
            path, path_on_filesystem=abs_path
        )
        if not resource_available:
            return None

        async with aiofiles.open(
            self.path_on_filesystem(path), mode="rb"
        ) as a_file:
            return await a_file.read()

    async def get_crypto(self, path):
        file_abspath = self.path_on_filesystem(path)
        crypto_file = f"{splitext(file_abspath)[0]}.txt"

        try:
            async with aiofiles.open(
                crypto_file, mode="r", encoding="utf-8"
            ) as a_file:
                return await a_file.read()
        except FileNotFoundError:
            return None

    async def get_detector_data(self, path):
        file_abspath = self.path_on_filesystem(path)
        path = f"{splitext(file_abspath)[0]}.detectors.txt"

        resource_available = await self.exists(path, path_on_filesystem=path)

        if not resource_available:
            return None

        async with aiofiles.open(path, mode="r", encoding="utf-8") as a_file:
            return loads(await a_file.read())

    def path_on_filesystem(self, path):
        digest = hashlib.sha1(path.encode("utf-8")).hexdigest()
        root_path = self.context.config.FILE_STORAGE_ROOT_PATH.rstrip("/")
        return f"{root_path}/{digest[:2]}/{digest[2:]}"

    async def exists(
        self, path, path_on_filesystem=None
    ):  # pylint: disable=arguments-differ
        if path_on_filesystem is None:
            path_on_filesystem = self.path_on_filesystem(path)

        try:
            file_mtime = await aiofiles.os.path.getmtime(path_on_filesystem)
        except FileNotFoundError:
            return False
        else:
            return not self.is_expired(file_mtime)

    async def remove(self, path):
        n_path = self.path_on_filesystem(path)
        return await aiofiles.os.remove(n_path)

    def is_expired(self, mtime):
        if self.context.config.STORAGE_EXPIRATION_SECONDS is None:
            return False
        timediff = datetime.now() - datetime.fromtimestamp(mtime)
        return (
            timediff.total_seconds()
            > self.context.config.STORAGE_EXPIRATION_SECONDS
        )
