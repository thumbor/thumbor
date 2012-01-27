#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from collections import defaultdict

from pyvows import Vows, expect

from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.storages.mixed_storage import Storage as MixedStorage
from fixtures.storage_fixture import get_context

class Storage(object):
    def __init__(self, security_key):
        self.storage = defaultdict(dict)
        self.security_key = security_key

    def put(self, path, contents):
        self.storage[path]['path'] = path
        self.storage[path]['contents'] = contents

    def put_crypto(self, path):
        self.storage[path]['crypto'] = self.security_key

    def put_detector_data(self, path, data):
        self.storage[path]['detector'] = data

    def get_crypto(self, path):
        if path not in self.storage:
            raise RuntimeError('%s was not found in storage' % path)

        return self.storage[path]['crypto']

    def get_detector_data(self, path):
        if path not in self.storage or 'detector' not in self.storage[path]:
            return None

        return self.storage[path]['detector']

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
            storage.put_detector_data('path1', 'detector')

            return storage

        class IncludesPath(Vows.Context):
            def should_record_path(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']['path']).to_equal('path1')

            def should_record_contents_on_file_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']['contents']).to_equal('contents')

            def should_get_contents(self, topic):
                contents = topic.get('path1')
                expect(contents).to_equal('contents')

            def should_not_record_crypto_on_file_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(file_storage.storage['path1']).not_to_include('crypto')

            def should_not_record_contents_on_crypto_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(crypto_storage.storage['path1']).not_to_include('contents')

            def should_record_crypto_on_crypto_storage(self, topic):
                file_storage, crypto_storage = topic.file_storage, topic.crypto_storage
                expect(crypto_storage.storage['path1']['crypto']).to_equal('security-key')

            def should_get_crypto(self, topic):
                contents = topic.get_crypto('path1')
                expect(contents).to_equal('security-key')

            def should_get_detector_data(self, topic):
                contents = topic.get_detector_data('path1')
                expect(contents).to_equal('detector')

    class GetFromConfig(Vows.Context):
        def topic(self, storages):
            context = get_context()
            file_storage, crypto_storage, detector_storage = storages
            storage = MixedStorage(context)

            return storage

        class GetData(Vows.Context):
            def topic(self, storage):
                return (storage, storage.get('path'))

            def should_have_proper_file_storage(self, topic):
                expect(topic[0].file_storage).to_be_instance_of(NoStorage)

            def should_be_null(self, topic):
                expect(topic[1]).to_be_null()

        class GetDetectorData(Vows.Context):
            def topic(self, storage):
                return (storage, storage.get_detector_data('path'))

            def should_have_proper_detector_storage(self, topic):
                expect(topic[0].detector_storage).to_be_instance_of(NoStorage)

            def should_be_null(self, topic):
                expect(topic[1]).to_be_null()

        class GetCrypto(Vows.Context):
            def topic(self, storage):
                return (storage, storage.get_crypto('path'))

            def should_have_proper_crypto_storage(self, topic):
                expect(topic[0].crypto_storage).to_be_instance_of(NoStorage)

            def should_be_null(self, topic):
                expect(topic[1]).to_be_null()
