#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Any, Optional

from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    def __init__(
        self,
        context: Any,
        file_storage: Optional[BaseStorage] = None,
        crypto_storage: Optional[BaseStorage] = None,
        detector_storage: Optional[BaseStorage] = None,
    ):
        BaseStorage.__init__(self, context)
        self.file_storage: Optional[BaseStorage] = file_storage
        self.crypto_storage: Optional[BaseStorage] = crypto_storage
        self.detector_storage: Optional[BaseStorage] = detector_storage

    async def initialize(self, context: Any) -> None:
        self.__init_file_storage()
        self.__init_crypto_storage()
        self.__init_detector_storage()

    def __init_file_storage(self) -> None:
        if self.file_storage is None:
            self.context.modules.importer.import_item(
                config_key="file_storage",
                item_value=self.context.config.MIXED_STORAGE_FILE_STORAGE,
                class_name="Storage",
            )
            self.file_storage = (
                self.context.modules.file_storage
            ) = self.context.modules.importer.file_storage(self.context)

    def __init_crypto_storage(self) -> None:
        if self.crypto_storage is None:
            self.context.modules.importer.import_item(
                config_key="crypto_storage",
                item_value=self.context.config.MIXED_STORAGE_CRYPTO_STORAGE,
                class_name="Storage",
            )
            self.crypto_storage = (
                self.context.modules.crypto_storage
            ) = self.context.modules.importer.crypto_storage(self.context)

    def __init_detector_storage(self) -> None:
        if self.detector_storage is None:
            self.context.modules.importer.import_item(
                config_key="detector_storage",
                item_value=self.context.config.MIXED_STORAGE_DETECTOR_STORAGE,
                class_name="Storage",
            )
            self.detector_storage = (
                self.context.modules.detector_storage
            ) = self.context.modules.importer.detector_storage(self.context)

    async def put(self, path: str, file_bytes: bytes) -> Optional[str]:
        return await self.file_storage.put(path, file_bytes)

    async def put_detector_data(self, path: str, data: str) -> Optional[str]:
        return await self.detector_storage.put_detector_data(path, data)

    async def put_crypto(self, path: str) -> Optional[str]:
        return await self.crypto_storage.put_crypto(path)

    async def get(self, path: str) -> Optional[str]:
        return await self.file_storage.get(path)

    async def get_crypto(self, path: str) -> Optional[str]:
        return await self.crypto_storage.get_crypto(path)

    async def get_detector_data(self, path) -> Optional[str]:
        return await self.detector_storage.get_detector_data(path)

    async def exists(self, path: str) -> bool:
        return await self.file_storage.exists(path)
