#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import exists, dirname, join
import random
import shutil

from pyvows import Vows, expect

import thumbor.storages.file_storage as Storage
from thumbor.storages.file_storage import Storage as FileStorage
from thumbor.context import Context
from thumbor.config import Config
from fixtures.storage_fixture import IMAGE_URL, SAME_IMAGE_URL, IMAGE_BYTES, get_server


@Vows.batch
class FileStorageVows(Vows.Context):
    class CreatesRootPathIfNoneFound(Vows.Context):
        def topic(self):
            config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/%s" % random.randint(1, 10000000))
            storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
            storage.ensure_dir(config.FILE_STORAGE_ROOT_PATH)
            return exists(config.FILE_STORAGE_ROOT_PATH)

        def should_exist(self, topic):
            expect(topic).to_be_true()

    class CanStoreImage(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
            storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            storage.get(IMAGE_URL % 1, callback)

        def should_be_in_catalog(self, topic):
            expect(topic[0]).not_to_be_null()
            expect(topic[0]).not_to_be_an_error()

    class CanStoreImagesInSameFolder(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
            root_path = join(config.FILE_STORAGE_ROOT_PATH, dirname(SAME_IMAGE_URL % 999))
            if exists(root_path):
                shutil.rmtree(root_path)

            old_exists = Storage.storages.exists
            Storage.storages.exists = lambda path: False
            try:
                storage = Storage.Storage(Context(config=config, server=get_server('ACME-SEC')))

                storage.put(SAME_IMAGE_URL % 998, IMAGE_BYTES)
                storage.put(SAME_IMAGE_URL % 999, IMAGE_BYTES)
            finally:
                Storage.storages.exists = old_exists

            storage.get(SAME_IMAGE_URL % 999, callback)

        def should_be_in_catalog(self, topic):
            expect(topic[0]).not_to_be_null()
            expect(topic[0]).not_to_be_an_error()

    class CanGetImage(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
            storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))

            storage.put(IMAGE_URL % 2, IMAGE_BYTES)
            storage.get(IMAGE_URL % 2, callback)

        def should_not_be_null(self, topic):
            expect(topic[0]).not_to_be_null()
            expect(topic[0]).not_to_be_an_error()

        def should_have_proper_bytes(self, topic):
            expect(topic[0]).to_equal(IMAGE_BYTES)

    class CryptoVows(Vows.Context):
        class RaisesIfInvalidConfig(Vows.Context):

            @Vows.capture_error
            def topic(self):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/", STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = FileStorage(Context(config=config, server=get_server('')))
                storage.put(IMAGE_URL % 3, IMAGE_BYTES)
                return storage.put_crypto(IMAGE_URL % 3)

            def should_be_an_error(self, topic):
                expect(topic).to_be_an_error_like(RuntimeError)
                expect(topic).to_have_an_error_message_of(
                    "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified"
                )

        class GettingCryptoForANewImageReturnsNone(Vows.Context):
            @Vows.async_topic
            def topic(self, callback):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/", STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
                storage.get_crypto(IMAGE_URL % 9999, callback)

            def should_be_null(self, topic):
                expect(topic[0]).to_be_null()

        class DoesNotStoreIfConfigSaysNotTo(Vows.Context):
            @Vows.async_topic
            def topic(self, callback):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
                storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
                storage.put(IMAGE_URL % 5, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 5)
                storage.get_crypto(IMAGE_URL % 5, callback)

            def should_be_null(self, topic):
                expect(topic[0]).to_be_null()

        class CanStoreCrypto(Vows.Context):
            @Vows.async_topic
            def topic(self, callback):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/", STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))

                storage.put(IMAGE_URL % 6, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 6)
                storage.get_crypto(IMAGE_URL % 6, callback)

            def should_not_be_null(self, topic):
                expect(topic[0]).not_to_be_null()
                expect(topic[0]).not_to_be_an_error()

            def should_have_proper_key(self, topic):
                expect(topic[0]).to_equal('ACME-SEC')

    class DetectorVows(Vows.Context):
        class CanStoreDetectorData(Vows.Context):
            @Vows.async_topic
            def topic(self, callback):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
                storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
                storage.put(IMAGE_URL % 7, IMAGE_BYTES)
                storage.put_detector_data(IMAGE_URL % 7, 'some-data')
                storage.get_detector_data(IMAGE_URL % 7, callback)

            def should_not_be_null(self, topic):
                expect(topic[0]).not_to_be_null()
                expect(topic[0]).not_to_be_an_error()

            def should_equal_some_data(self, topic):
                expect(topic[0]).to_equal('some-data')

        class ReturnsNoneIfNoDetectorData(Vows.Context):
            @Vows.async_topic
            def topic(self):
                config = Config(FILE_STORAGE_ROOT_PATH="/tmp/thumbor/file_storage/")
                storage = FileStorage(Context(config=config, server=get_server('ACME-SEC')))
                storage.get_detector_data(IMAGE_URL % 10000, callback)

            def should_not_be_null(self, topic):
                expect(topic[0]).to_be_null()
