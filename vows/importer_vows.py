#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.engines.pil import Engine as pil_engine
from thumbor.engines.gif import Engine as gif_engine
from thumbor.loaders import http_loader
from thumbor.storages.file_storage import Storage as file_storage
from thumbor.result_storages.file_storage import Storage as result_file_storage
from thumbor.detectors.face_detector import Detector as face_detector
from thumbor.detectors import feature_detector
from thumbor.filters.rgb import Filter as rgb_filter


test_data = [
    ('ENGINE', pil_engine),
    ('GIF_ENGINE', gif_engine),
    ('LOADER', http_loader),
    ('STORAGE', file_storage),
    ('UPLOAD_PHOTO_STORAGE', file_storage),
    ('RESULT_STORAGE', result_file_storage),
    ('DETECTORS', (face_detector,)),
    ('FILTERS', (rgb_filter,)),
]


@Vows.batch
class ImporterVows(Vows.Context):

    class AllConfigurationVows(Vows.Context):
        def topic(self):
            for data in test_data:
                complete_config = Config(
                    ENGINE=r'thumbor.engines.pil',
                    GIF_ENGINE=r'thumbor.engines.gif',
                    LOADER=r'thumbor.loaders.http_loader',
                    STORAGE=r'thumbor.storages.file_storage',
                    UPLOAD_PHOTO_STORAGE=r'thumbor.storages.file_storage',
                    RESULT_STORAGE=r'thumbor.result_storages.file_storage',
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

    class ImportWithFixedValueVows(Vows.Context):

        class SingleItem(Vows.Context):
            def topic(self):
                importer = Importer(None)
                importer.import_item(config_key='file_storage', item_value='thumbor.storages.file_storage', class_name='Storage')
                return importer.file_storage

            def should_equal_file_storage(self, topic):
                expect(topic).to_equal(file_storage)

        class MultipleItems(Vows.Context):
            def topic(self):
                importer = Importer(None)
                importer.import_item(
                    config_key='detectors', is_multiple=True,
                    item_value=(
                        'thumbor.detectors.feature_detector',
                        'thumbor.detectors.feature_detector'
                    )
                )
                return importer.detectors

            def should_have_length_of_2(self, topic):
                expect(topic).to_length(2)

            def should_contain_both_detectors(self, topic):
                expect(topic).to_include(feature_detector)
