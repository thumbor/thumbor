#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.storages.no_storage import Storage as NoStorage
from fixtures.storage_fixture import IMAGE_URL, IMAGE_BYTES


@Vows.batch
class NoStorageVows(Vows.Context):
    class CanStoreImage(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            storage = NoStorage(None)
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            storage.get(IMAGE_URL % 1, callback)

        def should_be_null(self, topic):
            expect(topic[0]).to_be_null()

    class KnowsNoImages(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            storage = NoStorage(None)
            storage.exists(IMAGE_URL % 1, callback)

        def should_be_false(self, topic):
            expect(topic[0]).to_be_false()

    class RemovesImage(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            storage = NoStorage(None)
            storage.remove(IMAGE_URL % 1, callback)

        def should_be_null(self, topic):
            expect(topic[0]).to_be_null()

    class StoresCrypto(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            storage = NoStorage(None)
            storage.put_crypto(IMAGE_URL % 2)
            storage.get_crypto(IMAGE_URL % 2, callback)

        def should_be_null(self, topic):
            expect(topic[0]).to_be_null()

    class DetectorData(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            storage = NoStorage(None)
            storage.put_detector_data(IMAGE_URL % 3, "some data")
            storage.get_detector_data(IMAGE_URL % 3, callback)

        def should_be_null(self, topic):
            expect(topic[0]).to_be_null()
