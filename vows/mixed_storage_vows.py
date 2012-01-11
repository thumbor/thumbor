#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from collections import defaultdict

from pyvows import Vows, expect

from thumbor.storages.mixed_storage import Storage as MixedStorage

class Storage(object):
    def __init__(self, security_key):
        self.storage = defaultdict(dict)
        self.security_key = security_key

    def put(self, path, contents):
        self.storage[path]['path'] = path
        self.storage[path]['contents'] = contents

    def put_crypto(self, path):
        self.storage[path]['crypto'] = self.security_key

    def get_crypto(self, path):
        if path not in self.storage:
            raise RuntimeError('%s was not found in storage' % path)

        return self.storage[path]['crypto']

    def get(self, path):
        if path not in self.storage:
            raise RuntimeError('%s was not found in storage' % path)

        return self.storage[path]['contents']

@Vows.batch
class MixedStorageVows(Vows.Context):
    def topic(self):
        return (Storage('security-key'), Storage('security-key'), Storage('detector'))

    class Put(Vows.Context):
        def topic(self, storages):
            file_storage, crypto_storage, detector_storage = storages
            storage = MixedStorage(None, file_storage, crypto_storage, detector_storage)
            storage.put('path1', 'contents')
            storage.put_crypto('path1')

            return storage

        class IncludesPath(Vows.Context):
            def should_record_path(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']['path']).to_equal('path1')

            def should_record_contents_on_file_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']['contents']).to_equal('contents')

            def should_not_record_crypto_on_file_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']).not_to_include('crypto')

            def should_not_record_contents_on_crypto_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(crypto_storage.storage['path1']).not_to_include('contents')

            def should_record_crypto_on_crypto_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(crypto_storage.storage['path1']['crypto']).to_equal('security-key')


