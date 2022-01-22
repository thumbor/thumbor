#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import thumbor.result_storages as storages
from thumbor.compatibility import compatibility_get


class Storage(storages.BaseStorage):
    @property
    def storage(self):
        storage = self.context.modules.compatibility_legacy_result_storage
        if storage is None:
            raise RuntimeError(
                "The 'COMPATIBILITY_LEGACY_RESULT_STORAGE' configuration should point "
                "to a valid result storage when using compatibility result storage."
            )
        return storage

    async def put(self, image_bytes):
        if self.storage is None:
            return
        return self.storage.put(image_bytes)

    async def get(self):
        if self.storage is None:
            return
        return await compatibility_get(func=self.storage.get)
