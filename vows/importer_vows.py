#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.importer import Importer
from thumbor.config import Config, ConfigurationError
from thumbor.engines.pil import Engine as pil_engine
from thumbor.loaders import http_loader
from thumbor.storages.file_storage import Storage as file_storage
from thumbor.detectors.face_detector import Detector as face_detector
from thumbor.filters.rgb import Filter as rgb_filter

test_data = [
    ('ENGINE', pil_engine),
    ('LOADER', http_loader),
    ('STORAGE', file_storage),
    ('DETECTORS', (face_detector,)),
    ('FILTERS', (rgb_filter,)),
]

@Vows.batch
class ImporterVows(Vows.Context):

    def topic(self):
        for data in test_data:
            complete_config = Config(
                ENGINE=r'thumbor.engines.pil',
                LOADER=r'thumbor.loaders.http_loader',
                STORAGE=r'thumbor.storages.file_storage',
                DETECTORS=['thumbor.detectors.face_detector'],
                FILTERS=['thumbor.filters.rgb']
            )

            yield data, complete_config

    class CanImportItem(Vows.Context):
        def topic(self, test_item):
            test_data, config = test_item
            importer = Importer(config)
            importer.import_modules()

            if hasattr(importer, test_data[0].lower()):
                return (getattr(importer, test_data[0].lower()), test_data[1])
            return (None, None)

        def should_be_proper_item(self, topic):
            if topic[0] is tuple:
                for index, item in enumerate(topic[0]):
                    expect(item).not_to_be_null()
                    expect(item).to_equal(topic[1][index])
            else:
                expect(topic[0]).not_to_be_null()
                expect(topic[0]).to_equal(topic[1])

    class ValidatesPresenceOfItem(Vows.Context):
        def topic(self, test_item):
            test_data, config = test_item
            delattr(config, test_data[0])
            Importer(config)

        def should_be_error(self, topic):
            expect(topic).to_be_an_error_like(ConfigurationError)
