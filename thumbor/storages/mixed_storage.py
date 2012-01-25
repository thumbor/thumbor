#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.storages import BaseStorage

class Storage(BaseStorage):
    def __init__(self, context, file_storage=None, crypto_storage=None, detector_storage=None):
        BaseStorage.__init__(self, context)

        self.file_storage = file_storage
        self._init_file_storage()

        self.crypto_storage = crypto_storage
        self._init_crypto_storage()

        self.detector_storage = detector_storage
        self._init_detector_storage()

    def _init_file_storage(self):
        if self.file_storage is None:
            self.context.modules.importer.import_item(
                config_key='file_storage',
                item_value=self.context.config.MIXED_STORAGE_FILE_STORAGE,
                class_name='Storage'
            )
            self.file_storage = self.context.modules.file_storage = self.context.modules.importer.file_storage(self.context)

    def _init_crypto_storage(self):
        if self.crypto_storage is None:
            self.context.modules.importer.import_item(
                config_key='crypto_storage',
                item_value=self.context.config.MIXED_STORAGE_CRYPTO_STORAGE,
                class_name='Storage'
            )
            self.crypto_storage = self.context.modules.crypto_storage = self.context.modules.importer.crypto_storage(self.context)

    def _init_detector_storage(self):
        if self.detector_storage is None:
            self.context.modules.importer.import_item(
                config_key='detector_storage',
                item_value=self.context.config.MIXED_STORAGE_DETECTOR_STORAGE,
                class_name='Storage'
            )
            self.detector_storage = self.context.modules.detector_storage = self.context.modules.importer.detector_storage(self.context)

    def put(self, path, bytes):
        self.file_storage.put(path, bytes)

    def put_detector_data(self, path, data):
        self.detector_storage.put_detector_data(path, data)

    def put_crypto(self, path):
        self.crypto_storage.put_crypto(path)

    def get_crypto(self, path):
        return self.crypto_storage.get_crypto(path)

    def get_detector_data(self, path):
        return self.detector_storage.get_detector_data(path)

    def get(self, path):
        return self.file_storage.get(path)
