#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor import storages
from thumbor.compatibility import compatibility_get


class Storage(storages.BaseStorage):
    @property
    def storage(self):
        storage = self.context.modules.compatibility_legacy_storage
        if storage is None:
            raise RuntimeError(
                "The 'COMPATIBILITY_LEGACY_STORAGE' configuration should point to "
                "a valid storage when using compatibility storage."
            )
        return storage

    async def put(self, path, file_bytes):
        return self.storage.put(path, file_bytes)

    async def put_crypto(self, path):
        return self.storage.put_crypto(path)

    async def put_detector_data(self, path, data):
        return self.storage.put_detector_data(path, data)

    async def get(self, path):
        return await compatibility_get(path, func=self.storage.get)

    async def get_crypto(self, path):
        return await compatibility_get(path, func=self.storage.get_crypto)

    async def get_detector_data(self, path):
        return await compatibility_get(
            path, func=self.storage.get_detector_data
        )

    async def exists(self, path, *args, **kw):
        return await compatibility_get(
            path, func=self.storage.exists, *args, **kw
        )

    async def remove(self, path):
        return self.storage.remove(path)
