#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    def __init__(
        self,
        context,
        file_storage=None,
        crypto_storage=None,
        detector_storage=None,
    ):
        BaseStorage.__init__(self, context)

        self.file_storage = file_storage

        self.crypto_storage = crypto_storage

        self.detector_storage = detector_storage

    def _init_file_storage(self):
        if self.file_storage is None:
            self.context.modules.importer.import_item(
                config_key="file_storage",
                item_value=self.context.config.MIXED_STORAGE_FILE_STORAGE,
                class_name="Storage",
            )
            self.file_storage = self.context.modules.file_storage = (
                self.context.modules.importer.file_storage(self.context)
            )

    def _init_crypto_storage(self):
        if self.crypto_storage is None:
            self.context.modules.importer.import_item(
                config_key="crypto_storage",
                item_value=self.context.config.MIXED_STORAGE_CRYPTO_STORAGE,
                class_name="Storage",
            )
            self.crypto_storage = self.context.modules.crypto_storage = (
                self.context.modules.importer.crypto_storage(self.context)
            )

    def _init_detector_storage(self):
        if self.detector_storage is None:
            self.context.modules.importer.import_item(
                config_key="detector_storage",
                item_value=self.context.config.MIXED_STORAGE_DETECTOR_STORAGE,
                class_name="Storage",
            )
            self.detector_storage = self.context.modules.detector_storage = (
                self.context.modules.importer.detector_storage(self.context)
            )

    async def put(self, path, file_bytes):
        self._init_file_storage()
        return await self.file_storage.put(path, file_bytes)

    async def put_detector_data(self, path, data):
        self._init_detector_storage()
        return await self.detector_storage.put_detector_data(path, data)

    async def put_crypto(self, path):
        self._init_crypto_storage()
        return await self.crypto_storage.put_crypto(path)

    async def get_crypto(self, path):
        self._init_crypto_storage()
        result = await self.crypto_storage.get_crypto(path)
        return result

    async def get_detector_data(self, path):
        self._init_detector_storage()
        result = await self.detector_storage.get_detector_data(path)
        return result

    async def get(self, path):
        self._init_file_storage()
        result = await self.file_storage.get(path)
        return result

    async def exists(self, path):
        self._init_file_storage()
        result = await self.file_storage.exists(path)
        return result

    def resolve_original_photo_path(self, request, filename):
        return self.file_storage.resolve_original_photo_path(request, filename)
