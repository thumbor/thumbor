#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from datetime import datetime, timedelta
from os.path import dirname

import pytz
from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.images import default_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithoutEtagsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_without_etags(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Etag")


class ImageOperationsWithoutCorsHeaderTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_cors_header(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include("Access-Control-Allow-Origin")


class ImageOperationsWithCorsHeaderTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(
            SECURITY_KEY="ACME-SEC", ACCESS_CONTROL_ALLOW_ORIGIN_HEADER="*"
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_with_cors_header(self):
        response = await self.async_fetch(
            "/unsafe/image.jpg", headers={"Accept": "image/webp,*/*;q=0.8"}
        )

        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Access-Control-Allow-Origin")
        expect(response.headers["Access-Control-Allow-Origin"]).to_equal("*")


class ImageOperationsWithLastModifiedTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = "thumbor.result_storages.file_storage"
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    def write_image(self):
        expected_path = self.result_storage.normalize_path(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )

        if not os.path.exists(dirname(expected_path)):
            os.makedirs(dirname(expected_path))

        if not os.path.exists(expected_path):
            with open(expected_path, "wb") as img:
                img.write(default_image())

    @gen_test
    async def test_can_get_304_with_last_modified(self):
        self.write_image()
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg",
            headers={
                "Accept": "image/webp,*/*;q=0.8",
                "If-Modified-Since": (datetime.utcnow() + timedelta(seconds=1))
                .replace(tzinfo=pytz.utc)
                .strftime("%a, %d %b %Y %H:%M:%S GMT"),  # NOW +1 sec UTC
            },
        )

        expect(response.code).to_equal(304)

    @gen_test
    async def test_can_get_image_with_last_modified(self):
        self.write_image()
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg",
            headers={
                "Accept": "image/webp,*/*;q=0.8",
                "If-Modified-Since": (datetime.utcnow() - timedelta(days=365))
                .replace(tzinfo=pytz.utc)
                .strftime("%a, %d %b %Y %H:%M:%S GMT"),  # Last Year
            },
        )

        expect(response.code).to_equal(200)
        expect(response.headers).to_include("Last-Modified")
