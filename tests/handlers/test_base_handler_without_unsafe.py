# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import assert_similar_to
from tests.fixtures.images import default_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class ImageOperationsWithoutUnsafeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8890, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_can_get_image_with_signed_url(self):
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg"
        )
        assert response.code == 200
        assert_similar_to(response.body, default_image())

    @gen_test
    async def test_getting_unsafe_image_fails(self):
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        assert response.code == 400

    @gen_test
    async def test_hash_injection_in_image_path_is_rejected(self):
        # Hash for 'smart/image.jpg' with key ACME-SEC is
        # _wIUeSaeHw8dricKG2MGhqu5thk=.  By duplicating that hash inside the
        # image path the vulnerable str.replace() would strip both occurrences
        # and reconstruct 'smart/image.jpg', making validation pass for a URL
        # that actually points at a different resource.
        #
        # Attack URL structure: /{hash}/sma/{hash}/rt/image.jpg
        # Vulnerable code: removes all /{hash}/ → "sma" + "rt/image.jpg"
        #                  = "smart/image.jpg" → validates incorrectly.
        # Fixed code: strips only the leading /{hash}/ → validates
        #             "sma/_wIUeSaeHw8dricKG2MGhqu5thk=/rt/image.jpg"
        #             which does not match the original signature.
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk="
            "/sma"
            "/_wIUeSaeHw8dricKG2MGhqu5thk="
            "/rt/image.jpg"
        )
        assert response.code == 400

    @gen_test
    async def test_url_encoded_hash_injection_in_image_path_is_rejected(self):
        # Same bypass using the URL-percent-encoded hash (%3D instead of =).
        # The vulnerable code performed a second str.replace() for the quoted
        # form, so inserting the quoted hash between the two halves of the
        # plain hash also collapsed to the original signed URL.
        response = await self.async_fetch(
            "/_wIUeSaeHw8dricKG2MGhqu5thk="
            "/sma"
            "/_wIUeSaeHw8dricKG2MGhqu5thk%3D"
            "/rt/image.jpg"
        )
        assert response.code == 400
