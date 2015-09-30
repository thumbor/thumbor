#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.storages.no_storage import Storage as NoStorage
from fixtures.storage_fixture import IMAGE_URL, IMAGE_BYTES


@Vows.batch
class NoStorageVows(Vows.Context):
    class CanStoreImage(Vows.Context):
        def topic(self):
            storage = NoStorage(None)
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            return storage.get(IMAGE_URL % 1)

        def should_be_null(self, topic):
            expect(topic.result()).to_be_null()

    class KnowsNoImages(Vows.Context):
        def topic(self):
            storage = NoStorage(None)
            return storage.exists(IMAGE_URL % 1)

        def should_be_false(self, topic):
            expect(topic.result()).to_be_false()

    class RemovesImage(Vows.Context):
        def topic(self):
            storage = NoStorage(None)
            return storage.remove(IMAGE_URL % 1)

        def should_be_null(self, topic):
            expect(topic).to_be_null()

    class StoresCrypto(Vows.Context):
        def topic(self):
            storage = NoStorage(None)
            storage.put_crypto(IMAGE_URL % 2)

            return storage.get_crypto(IMAGE_URL % 2)

        def should_be_null(self, topic):
            expect(topic.result()).to_be_null()

    class DetectorData(Vows.Context):
        def topic(self):
            storage = NoStorage(None)
            storage.put_detector_data(IMAGE_URL % 3, "some data")
            return storage.get_detector_data(IMAGE_URL % 3)

        def should_be_null(self, topic):
            expect(topic.result()).to_be_null()
