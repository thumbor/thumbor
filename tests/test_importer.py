#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

import thumbor.handler_lists.healthcheck as healthcheck_handler_list
from tests.base import TestCase
from thumbor.config import Config
from thumbor.detectors import feature_detector
from thumbor.detectors.face_detector import Detector as face_detector
from thumbor.engines.gif import Engine as gif_engine
from thumbor.engines.pil import Engine as pil_engine
from thumbor.filters.rgb import Filter as rgb_filter
from thumbor.importer import Importer
from thumbor.loaders import http_loader
from thumbor.result_storages.file_storage import Storage as result_file_storage
from thumbor.storages.file_storage import Storage as file_storage


class ImporterTestCase(TestCase):
    def get_config(self):
        return Config(
            ENGINE="thumbor.engines.pil",
            GIF_ENGINE="thumbor.engines.gif",
            LOADER="thumbor.loaders.http_loader",
            STORAGE="thumbor.storages.file_storage",
            UPLOAD_PHOTO_STORAGE="thumbor.storages.file_storage",
            RESULT_STORAGE="thumbor.result_storages.file_storage",
            DETECTORS=["thumbor.detectors.face_detector"],
            FILTERS=["thumbor.filters.rgb"],
            HANDLER_LISTS=["thumbor.handler_lists.healthcheck"],
        )

    def test_import_item_should_be_proper_item(self):
        importer = Importer(self.get_config())
        importer.import_modules()
        data = {
            "ENGINE": pil_engine,
            "GIF_ENGINE": gif_engine,
            "LOADER": http_loader,
            "STORAGE": file_storage,
            "UPLOAD_PHOTO_STORAGE": file_storage,
            "RESULT_STORAGE": result_file_storage,
            "DETECTORS": (face_detector,),
            "FILTERS": (rgb_filter,),
            "HANDLER_LISTS": (healthcheck_handler_list,),
        }

        for key, value in data.items():
            prop, default_value = (None, None)
            if hasattr(importer, key.lower()):
                prop, default_value = (getattr(importer, key.lower()), value)

            if prop is tuple:
                for index, item in enumerate(prop):
                    expect(item).not_to_be_null().to_equal(
                        default_value[index]
                    )
            else:
                expect(prop).not_to_be_null().to_equal(default_value)

    @staticmethod
    def test_single_item_should_equal_file_storage():
        importer = Importer(None)
        importer.import_item(
            config_key="file_storage",
            item_value="thumbor.storages.file_storage",
            class_name="Storage",
        )
        expect(getattr(importer, "file_storage")).to_equal(file_storage)

    @staticmethod
    def test_multiple_items_can_be_imported():
        importer = Importer(None)
        importer.import_item(
            config_key="detectors",
            is_multiple=True,
            item_value=(
                "thumbor.detectors.feature_detector",
                "thumbor.detectors.feature_detector",
            ),
        )

        expect(importer.detectors).to_length(2)
        expect(importer.detectors).to_include(feature_detector)
