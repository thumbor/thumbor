#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re
import tempfile
from shutil import rmtree

from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.images import (
    TOO_SMALL_IMAGE_PATH,
    VALID_IMAGE_PATH,
    too_heavy_image,
    too_small_image,
    valid_image,
)
from thumbor.config import Config
from thumbor.context import Context
from thumbor.importer import Importer


class UploadTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_path = tempfile.mkdtemp()
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.root_path)

    @property
    def upload_storage(self):
        return self.context.modules.upload_photo_storage

    def get_path_from_location(self, location):
        return "/".join(location.lstrip("/").rstrip("/").split("/")[1:-1])

    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)


class UploadAPINewFileTestCase(UploadTestCase):
    @gen_test
    async def test_can_post_image_with_content_type(self):
        filename = "new_image_with_a_filename.jpg"
        response = await self.async_post(
            self.base_uri,
            {"Content-Type": "image/jpeg", "Slug": filename},
            valid_image(),
        )

        expect(response.code).to_equal(201)

        expect(response.headers).to_include("Location")
        expect(response.headers["Location"]).to_match(
            self.base_uri + r"/[^\/]{32}/" + filename
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_with_charset(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri,
            {"Content-Type": "image/jpeg;charset=UTF-8"},
            valid_image(),
        )

        expect(response.code).to_equal(201)

        expect(response.headers).to_include("Location")
        expect(response.headers["Location"]).to_match(
            self.base_uri + r"/[^\/]{32}/" + filename
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_with_unknown_charset(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri,
            {"Content-Type": "image/thisIsAUnknwonOrBadlyFormedCHarset"},
            valid_image(),
        )

        expect(response.code).to_equal(201)

        expect(response.headers).to_include("Location")
        expect(response.headers["Location"]).to_match(
            self.base_uri + r"/[^\/]{32}/" + filename
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_without_filename(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )

        expect(response.code).to_equal(201)

        expect(response.headers).to_include("Location")
        expect(response.headers["Location"]).to_match(
            self.base_uri + r"/[^\/]{32}/" + filename
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_from_html_form(self):
        filename = "crocodile2.jpg"
        image = ("media", filename, valid_image())
        response = await self.async_post_files(
            self.base_uri, {"Slug": b"another_filename.jpg"}, (image,)
        )

        expect(response.code).to_equal(201)

        expect(response.headers).to_include("Location")
        expect(response.headers["Location"]).to_match(
            self.base_uri + r"/[^\/]{32}/" + filename
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)


class UploadAPIUpdateFileTestCase(UploadTestCase):
    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = True
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_can_modify_existing_image(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        location = response.headers["Location"]
        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, too_small_image()
        )

        expect(response.code).to_equal(204)

        id_should_exist = (
            re.compile(self.base_uri + r"/([^\/]{32})/" + filename)
            .search(location)
            .group(1)
        )
        expected_path = self.upload_storage.path_on_filesystem(id_should_exist)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(TOO_SMALL_IMAGE_PATH)

        id_shouldnt_exist = (
            re.compile(self.base_uri + r"/(.*)").search(location).group(1)
        )
        expected_path = self.upload_storage.path_on_filesystem(
            id_shouldnt_exist
        )
        expect(expected_path).not_to_exist()


class UploadAPIUpdateSmallIdFileTestCase(UploadTestCase):
    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = False
        cfg.UPLOAD_PUT_ALLOWED = True
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename
        cfg.MAX_ID_LENGTH = 36

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_cant_get_truncated_id_when_stored_with_large_id(self):
        image_id = "e5bcf126-791b-4375-9f73-925ab8b9fb5f"
        path = f"/image/{image_id}"

        response = await self.async_put(
            path, {"Content-Type": "image/jpeg"}, valid_image()
        )
        expect(response.code).to_equal(204)

        response = await self.async_get(
            path[: 7 + 32], {"Accept": "image/jpeg"}
        )
        expect(response.code).to_equal(404)

    @gen_test
    async def test_can_get_actual_id_when_stored_with_large_id(self):
        path = "/image/e5bcf126-791b-4375-9f73-925ab8b9fb5g"

        await self.async_put(
            path, {"Content-Type": "image/jpeg"}, valid_image()
        )
        response = await self.async_get(
            path + "123456", {"Accept": "image/jpeg"}
        )

        expect(response.code).to_equal(200)

        expect(response.body).to_be_similar_to(valid_image())


class UploadAPIDeleteTestCase(UploadTestCase):
    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = True
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_can_delete_existing_image(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        expect(response.code).to_equal(201)

        location = response.headers["Location"]
        image_id = (
            re.compile(self.base_uri + r"/([^\/]{32})/" + filename)
            .search(location)
            .group(1)
        )
        image_location = self.upload_storage.path_on_filesystem(image_id)
        expect(image_location).to_exist()

        response = await self.async_delete(location, {})
        expect(response.code).to_equal(204)

        expect(image_location).not_to_exist()

    @gen_test
    async def test_deleting_unknown_image_returns_not_found(self):
        uri = self.base_uri + "/an/unknown/image"
        response = await self.async_delete(uri, {})
        expect(response.code).to_equal(404)


class UploadAPIRetrieveTestCase(UploadTestCase):
    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DELETE_ALLOWED = True
        cfg.UPLOAD_PUT_ALLOWED = False
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename

        importer = Importer(cfg)
        importer.import_modules()

        return Context(None, cfg, importer)

    @gen_test
    async def test_can_retrieve_existing_image(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        expect(response.code).to_equal(201)

        location = response.headers["Location"]
        response = await self.async_get(location, {"Accept": "image/jpeg"})
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(valid_image())
        expect(response.headers["Content-Type"]).to_equal("image/jpeg")

    @gen_test
    async def test_retrieving_unknown_image_returns_not_found(self):
        uri = self.base_uri + "/an/unknown/image"
        response = await self.async_get(uri, {"Accept": "image/jpeg"})
        expect(response.code).to_equal(404)


class UploadAPIValidationTestCase(UploadTestCase):
    """
    Validation :
        - Invalid image
        - Size constraints
        - Weight constraints
    """

    def get_context(self):
        self.default_filename = "image"

        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PUT_ALLOWED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_DEFAULT_FILENAME = self.default_filename
        cfg.MIN_WIDTH = 40
        cfg.MIN_HEIGHT = 40
        cfg.UPLOAD_MAX_SIZE = 72000

        importer = Importer(cfg)
        importer.import_modules()
        return Context(None, cfg, importer)

    @gen_test
    async def test_posting_invalid_image_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, "invalid image"
        )
        expect(response.code).to_equal(415)

    @gen_test
    async def test_posting_invalid_image_through_html_form_fails(self):
        image = ("media", "crocodile9999.jpg", b"invalid image")
        response = await self.async_post_files(self.base_uri, {}, (image,))
        expect(response.code).to_equal(415)

    @gen_test
    async def test_modifying_existing_image_to_invalid_image(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        expect(response.code).to_equal(201)
        location = response.headers["Location"]

        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, "invalid image"
        )
        expect(response.code).to_equal(415)

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_posting_a_too_small_image_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, too_small_image()
        )
        expect(response.code).to_equal(412)

    @gen_test
    async def test_posting_a_too_small_image_from_html_form_fails(self):
        image = ("media", "crocodile9999.jpg", too_small_image())
        response = await self.async_post_files(self.base_uri, {}, (image,))
        expect(response.code).to_equal(412)

    @gen_test
    async def test_modifying_existing_image_to_small_image(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        expect(response.code).to_equal(201)

        location = response.headers["Location"]
        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, too_small_image()
        )
        expect(response.code).to_equal(412)

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)

    @gen_test
    async def test_posting_an_image_too_heavy_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, too_heavy_image()
        )
        expect(response.code).to_equal(412)

    @gen_test
    async def test_posting_an_image_too_heavy_through_an_html_form_fails(self):
        image = ("media", "oversized9999.jpg", too_heavy_image())
        response = await self.async_post_files(self.base_uri, {}, (image,))
        expect(response.code).to_equal(412)

    @gen_test
    async def test_modifying_existing_image_to_heavy_image_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        location = response.headers["Location"]

        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, too_heavy_image()
        )
        expect(response.code).to_equal(412)

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        expect(expected_path).to_exist()
        expect(expected_path).to_be_the_same_as(VALID_IMAGE_PATH)
