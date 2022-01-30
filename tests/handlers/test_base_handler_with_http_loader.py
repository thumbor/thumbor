#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from shutil import which
from urllib.parse import quote

from libthumbor import CryptoURL
from preggy import expect
from tornado.testing import gen_test

from tests.base import normalize_unicode_path
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines

JPEGTRAN_AVAILABLE = which("jpegtran") is not None
EXIFTOOL_AVAILABLE = which("exiftool") is not None


class ImagingOperationsWithHttpLoaderTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.http_loader"
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_image_already_generated_by_thumbor(self):
        with open("./tests/fixtures/images/image.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/smart/image.jpg"), fixture.read()
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            crypto.generate(image_url=quote("http://test.com/smart/image.jpg"))
        )
        url = crypto.generate(image_url=quote(image_url))

        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_already_generated_by_thumbor_2_times(self):
        with open(
            normalize_unicode_path(
                "./tests/fixtures/images/alabama1_ap620é.jpg"
            ),
            "rb",
        ) as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/smart/alabama1_ap620é"), fixture.read()
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            crypto.generate(
                image_url=quote(
                    self.get_url(
                        crypto.generate(
                            image_url=quote(
                                "http://test.com/smart/alabama1_ap620é"
                            )
                        )
                    )
                )
            )
        )

        url = crypto.generate(image_url=quote(image_url))

        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_with_utf8_url(self):
        with open("./tests/fixtures/images/maracujá.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/maracujá.jpg".encode("utf-8")),
                fixture.read(),
            )
        crypto = CryptoURL("ACME-SEC")
        image_url = self.get_url(
            quote("/unsafe/http://test.com/maracujá.jpg".encode("utf-8"))
        )
        url = crypto.generate(image_url=quote(image_url))
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)

    @gen_test
    async def test_image_with_http_utf8_url(self):
        with open("./tests/fixtures/images/maracujá.jpg", "rb") as fixture:
            await self.context.modules.storage.put(
                quote("http://test.com/maracujá.jpg".encode("utf-8")),
                fixture.read(),
            )

        url = quote("/unsafe/http://test.com/maracujá.jpg".encode("utf-8"))
        response = await self.async_fetch(url)
        expect(response.code).to_equal(200)
