# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
import re
import tempfile
from os.path import exists, join
from pathlib import Path
from shutil import rmtree
from unittest import mock

from tornado.testing import gen_test

from tests.base import (
    TestCase,
    assert_exists,
    assert_same_as,
    assert_similar_to,
)
from tests.fixtures.images import (
    TOO_SMALL_IMAGE_PATH,
    VALID_IMAGE_PATH,
    too_heavy_image,
    too_small_image,
    valid_image,
)
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

UPLOAD_TOKEN = "first-upload-token-0123456789abcdef"
SECOND_UPLOAD_TOKEN = "second-upload-token-0123456789abcdef"


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

        assert response.code == 201

        assert "Location" in response.headers
        assert re.search(
            self.base_uri + r"/[^\/]{32}/" + filename,
            response.headers["Location"],
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_with_query_string(self):
        response = await self.async_post(
            self.base_uri + "?foo=bar",
            {"Content-Type": "image/jpeg", "Slug": "photo.jpg"},
            valid_image(),
        )

        assert response.code == 201
        location = response.headers["Location"]
        assert re.fullmatch(
            self.base_uri + r"/[0-9a-f]{32}/photo\.jpg", location
        )

        response = await self.async_get(location)
        assert response.code == 200
        assert_similar_to(response.body, valid_image())

    @gen_test
    async def test_can_post_image_with_charset(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri,
            {"Content-Type": "image/jpeg;charset=UTF-8"},
            valid_image(),
        )

        assert response.code == 201

        assert "Location" in response.headers
        assert re.search(
            self.base_uri + r"/[^\/]{32}/" + filename,
            response.headers["Location"],
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_with_unknown_charset(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri,
            {"Content-Type": "image/thisIsAUnknwonOrBadlyFormedCHarset"},
            valid_image(),
        )

        assert response.code == 201

        assert "Location" in response.headers
        assert re.search(
            self.base_uri + r"/[^\/]{32}/" + filename,
            response.headers["Location"],
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_image_without_filename(self):
        filename = self.default_filename + ".jpg"
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )

        assert response.code == 201

        assert "Location" in response.headers
        assert re.search(
            self.base_uri + r"/[^\/]{32}/" + filename,
            response.headers["Location"],
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_from_html_form(self):
        filename = "crocodile2.jpg"
        image = ("media", filename, valid_image())
        response = await self.async_post_files(
            self.base_uri, {"Slug": b"another_filename.jpg"}, (image,)
        )

        assert response.code == 201

        assert "Location" in response.headers
        assert re.search(
            self.base_uri + r"/[^\/]{32}/" + filename,
            response.headers["Location"],
        )

        expected_path = self.get_path_from_location(
            response.headers["Location"]
        )
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_can_post_from_html_form_with_url_encoded_filename(self):
        filenames = (
            ("gru\u0308n.jpg", "gru%CC%88n.jpg"),
            ("grün.jpg", "gr%C3%BCn.jpg"),
            ("猫.jpg", "%E7%8C%AB.jpg"),
            ("photo #1?100%/crop.jpg", "photo%20%231%3F100%25%2Fcrop.jpg"),
            ("photo%20name.jpg", "photo%2520name.jpg"),
        )
        for filename, encoded_filename in filenames:
            with self.subTest(filename=filename):
                response = await self.async_post_files(
                    self.base_uri,
                    files=(("media", filename, valid_image()),),
                )

                assert response.code == 201
                location = response.headers["Location"]
                assert re.fullmatch(
                    self.base_uri
                    + r"/[0-9a-f]{32}/"
                    + re.escape(encoded_filename),
                    location,
                )

                response = await self.async_get(location)
                assert response.code == 200
                assert_similar_to(response.body, valid_image())

    @gen_test
    async def test_can_post_from_html_form_with_unencodable_filename(self):
        # UTF-7 "+2AA-" decodes to the lone surrogate U+D800.
        body = (
            b"--boundary\r\n"
            b'Content-Disposition: form-data; name="media"; '
            b"filename*=utf-7''%2B2AA-.jpg\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + valid_image()
            + b"\r\n--boundary--\r\n"
        )
        response = await self.async_fetch(
            self.base_uri,
            method="POST",
            body=body,
            headers={"Content-Type": "multipart/form-data; boundary=boundary"},
        )

        assert response.code == 201
        location = response.headers["Location"]
        assert re.fullmatch(
            self.base_uri + r"/[0-9a-f]{32}/%3F\.jpg", location
        )

        response = await self.async_get(location)
        assert response.code == 200
        assert_similar_to(response.body, valid_image())

    @gen_test
    async def test_can_post_image_with_non_ascii_slug(self):
        slugs = (
            ("gr%C3%BCn.jpg", "gr%C3%BCn.jpg"),
            ("grün.jpg".encode("utf-8").decode("latin1"), "gr%C3%BCn.jpg"),
            ("gr\xfcn.jpg", "gr%EF%BF%BDn.jpg"),
            ("gr%FCn.jpg", "gr%EF%BF%BDn.jpg"),
            ("photo #1?100%.jpg", "photo%20%231%3F100%25.jpg"),
        )
        for slug, encoded_filename in slugs:
            with self.subTest(slug=slug):
                response = await self.async_post(
                    self.base_uri,
                    {"Content-Type": "image/jpeg", "Slug": slug},
                    valid_image(),
                )

                assert response.code == 201
                location = response.headers["Location"]
                assert re.fullmatch(
                    self.base_uri
                    + r"/[0-9a-f]{32}/"
                    + re.escape(encoded_filename),
                    location,
                )

                response = await self.async_get(location)
                assert response.code == 200
                assert_similar_to(response.body, valid_image())

    @gen_test
    async def test_can_post_image_with_dot_segment_slug(self):
        for slug in (".", "..", "%2E%2E"):
            with self.subTest(slug=slug):
                response = await self.async_post(
                    self.base_uri,
                    {"Content-Type": "image/jpeg", "Slug": slug},
                    valid_image(),
                )

                assert response.code == 201
                assert re.fullmatch(
                    self.base_uri
                    + r"/[0-9a-f]{32}/"
                    + re.escape(self.default_filename + ".jpg"),
                    response.headers["Location"],
                )


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

        assert response.code == 204

        id_should_exist = (
            re.compile(self.base_uri + r"/([^\/]{32})/" + filename)
            .search(location)
            .group(1)
        )
        expected_path = self.upload_storage.path_on_filesystem(id_should_exist)
        assert_exists(expected_path)
        assert_same_as(expected_path, TOO_SMALL_IMAGE_PATH)

        id_shouldnt_exist = (
            re.compile(self.base_uri + r"/(.*)").search(location).group(1)
        )
        expected_path = self.upload_storage.path_on_filesystem(
            id_shouldnt_exist
        )
        assert not exists(expected_path)


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
        assert response.code == 204

        response = await self.async_get(
            path[: 7 + 32], {"Accept": "image/jpeg"}
        )
        assert response.code == 404

    @gen_test
    async def test_can_get_actual_id_when_stored_with_large_id(self):
        path = "/image/e5bcf126-791b-4375-9f73-925ab8b9fb5g"

        await self.async_put(
            path, {"Content-Type": "image/jpeg"}, valid_image()
        )
        response = await self.async_get(
            path + "123456", {"Accept": "image/jpeg"}
        )

        assert response.code == 200

        assert_similar_to(response.body, valid_image())


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
        assert response.code == 201

        location = response.headers["Location"]
        image_id = (
            re.compile(self.base_uri + r"/([^\/]{32})/" + filename)
            .search(location)
            .group(1)
        )
        image_location = self.upload_storage.path_on_filesystem(image_id)
        assert_exists(image_location)

        response = await self.async_delete(location, {})
        assert response.code == 204

        assert not exists(image_location)

    @gen_test
    async def test_deleting_unknown_image_returns_not_found(self):
        uri = self.base_uri + "/an/unknown/image"
        response = await self.async_delete(uri, {})
        assert response.code == 404


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
        assert response.code == 201

        location = response.headers["Location"]
        response = await self.async_get(location, {"Accept": "image/jpeg"})
        assert response.code == 200
        assert_similar_to(response.body, valid_image())
        assert response.headers["Content-Type"] == "image/jpeg"

    @gen_test
    async def test_retrieving_unknown_image_returns_not_found(self):
        uri = self.base_uri + "/an/unknown/image"
        response = await self.async_get(uri, {"Accept": "image/jpeg"})
        assert response.code == 404


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
        assert response.code == 415

    @gen_test
    async def test_posting_invalid_image_through_html_form_fails(self):
        image = ("media", "crocodile9999.jpg", b"invalid image")
        response = await self.async_post_files(self.base_uri, {}, (image,))
        assert response.code == 415

    @gen_test
    async def test_modifying_existing_image_to_invalid_image(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        assert response.code == 201
        location = response.headers["Location"]

        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, "invalid image"
        )
        assert response.code == 415

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_posting_a_too_small_image_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, too_small_image()
        )
        assert response.code == 412

    @gen_test
    async def test_posting_a_too_small_image_from_html_form_fails(self):
        image = ("media", "crocodile9999.jpg", too_small_image())
        response = await self.async_post_files(self.base_uri, {}, (image,))
        assert response.code == 412

    @gen_test
    async def test_modifying_existing_image_to_small_image(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        assert response.code == 201

        location = response.headers["Location"]
        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, too_small_image()
        )
        assert response.code == 412

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)

    @gen_test
    async def test_posting_an_image_too_heavy_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, too_heavy_image()
        )
        assert response.code == 412

    @gen_test
    async def test_posting_an_image_too_heavy_through_an_html_form_fails(self):
        image = ("media", "oversized9999.jpg", too_heavy_image())
        response = await self.async_post_files(self.base_uri, {}, (image,))
        assert response.code == 412

    @gen_test
    async def test_modifying_existing_image_to_heavy_image_fails(self):
        response = await self.async_post(
            self.base_uri, {"Content-Type": "image/jpeg"}, valid_image()
        )
        location = response.headers["Location"]

        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, too_heavy_image()
        )
        assert response.code == 412

        expected_path = self.get_path_from_location(location)
        expected_path = self.upload_storage.path_on_filesystem(expected_path)
        assert_exists(expected_path)
        assert_same_as(expected_path, VALID_IMAGE_PATH)


class UploadAPIAuthTestCase(UploadTestCase):
    upload_put_allowed = True
    upload_delete_allowed = True
    upload_auth_tokens = (UPLOAD_TOKEN, SECOND_UPLOAD_TOKEN)

    def get_context(self):
        cfg = Config()
        cfg.UPLOAD_ENABLED = True
        cfg.UPLOAD_PHOTO_STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.UPLOAD_PUT_ALLOWED = self.upload_put_allowed
        cfg.UPLOAD_DELETE_ALLOWED = self.upload_delete_allowed
        cfg.UPLOAD_AUTH_REQUIRED = True
        cfg.UPLOAD_AUTH_TOKENS = list(self.upload_auth_tokens)
        cfg.SECURITY_KEY = "upload-auth-test-security-key"

        importer = Importer(cfg)
        importer.import_modules()

        return Context(self.server, cfg, importer)

    def stored_files(self):
        return sorted(
            path for path in Path(self.root_path).rglob("*") if path.is_file()
        )

    async def post_image(self, authorization=None):
        headers = {"Content-Type": "image/jpeg"}
        if authorization is not None:
            headers["Authorization"] = authorization
        return await self.async_post(self.base_uri, headers, valid_image())

    async def post_authorized_image(self):
        response = await self.post_image(f"Bearer {UPLOAD_TOKEN}")
        assert response.code == 201
        return response.headers["Location"]

    def assert_unauthorized(self, response, invalid_token=False):
        assert response.code == 401
        challenge = 'Bearer realm="thumbor-upload"'
        if invalid_token:
            challenge += ', error="invalid_token"'
        assert response.headers["WWW-Authenticate"] == challenge
        assert response.body == b""


class UploadAPIRequiredAuthTestCase(UploadAPIAuthTestCase):
    @gen_test
    async def test_post_without_token_is_unauthorized(self):
        files_before = self.stored_files()

        response = await self.post_image()

        self.assert_unauthorized(response)
        assert self.stored_files() == files_before

    @gen_test
    async def test_form_post_without_token_is_unauthorized(self):
        files_before = self.stored_files()
        image = ("media", "croco.jpg", valid_image())

        response = await self.async_post_files(self.base_uri, {}, (image,))

        self.assert_unauthorized(response)
        assert self.stored_files() == files_before

    @gen_test
    async def test_post_with_wrong_token_is_unauthorized(self):
        files_before = self.stored_files()

        response = await self.post_image("Bearer wrong-upload-token")

        self.assert_unauthorized(response, invalid_token=True)
        assert self.stored_files() == files_before

    @gen_test
    async def test_post_with_another_scheme_is_unauthorized(self):
        for authorization in (f"Basic {UPLOAD_TOKEN}", UPLOAD_TOKEN, "Bearer"):
            with self.subTest(authorization=authorization):
                response = await self.post_image(authorization)

                self.assert_unauthorized(response)

    @gen_test
    async def test_post_with_non_ascii_token_is_unauthorized(self):
        response = await self.post_image("Bearer tok\u00e9n")

        self.assert_unauthorized(response, invalid_token=True)

    @gen_test
    async def test_post_with_security_key_is_unauthorized(self):
        security_key = self.context.config.SECURITY_KEY
        for authorization in (security_key, f"Bearer {security_key}"):
            with self.subTest(authorization=authorization):
                response = await self.post_image(authorization)

                assert response.code == 401

    @gen_test
    async def test_post_with_any_configured_token(self):
        for authorization in (
            f"Bearer {UPLOAD_TOKEN}",
            f"Bearer {SECOND_UPLOAD_TOKEN}",
            f"bearer {UPLOAD_TOKEN}",
        ):
            with self.subTest(authorization=authorization):
                response = await self.post_image(authorization)

                assert response.code == 201
                assert "WWW-Authenticate" not in response.headers

    @gen_test
    async def test_unauthorized_post_does_not_load_the_image(self):
        engine = self.context.modules.engine
        with mock.patch.object(engine, "load") as load_mock:
            response = await self.post_image("Bearer wrong-upload-token")

        assert response.code == 401
        load_mock.assert_not_called()

    @gen_test
    async def test_token_is_not_logged(self):
        with self.assertLogs(level=logging.DEBUG) as logs:
            response = await self.post_image("Bearer wrong-upload-token")

        assert response.code == 401
        output = "\n".join(logs.output)
        assert "wrong-upload-token" not in output
        assert UPLOAD_TOKEN not in output

    @gen_test
    async def test_put_requires_a_token(self):
        location = await self.post_authorized_image()
        image_path = self.upload_storage.path_on_filesystem(
            self.get_path_from_location(location)
        )

        for authorization in (None, "Bearer wrong-upload-token"):
            with self.subTest(authorization=authorization):
                headers = {"Content-Type": "image/jpeg"}
                if authorization is not None:
                    headers["Authorization"] = authorization
                response = await self.async_put(
                    location, headers, too_small_image()
                )

                assert response.code == 401
                assert_same_as(image_path, VALID_IMAGE_PATH)

        response = await self.async_put(
            location,
            {
                "Content-Type": "image/jpeg",
                "Authorization": f"Bearer {SECOND_UPLOAD_TOKEN}",
            },
            too_small_image(),
        )

        assert response.code == 204
        assert_same_as(image_path, TOO_SMALL_IMAGE_PATH)

    @gen_test
    async def test_delete_requires_a_token(self):
        location = await self.post_authorized_image()
        image_path = self.upload_storage.path_on_filesystem(
            self.get_path_from_location(location)
        )

        for headers in ({}, {"Authorization": "Bearer wrong-upload-token"}):
            with self.subTest(headers=headers):
                response = await self.async_delete(location, headers)

                assert response.code == 401
                assert_exists(image_path)

        response = await self.async_delete(
            location, {"Authorization": f"Bearer {UPLOAD_TOKEN}"}
        )

        assert response.code == 204
        assert not exists(image_path)

    @gen_test
    async def test_get_and_head_do_not_require_a_token(self):
        location = await self.post_authorized_image()

        response = await self.async_get(location, {"Accept": "image/jpeg"})
        assert response.code == 200
        assert_similar_to(response.body, valid_image())

        response = await self.async_fetch(location, method="HEAD")
        assert response.code == 200


class UploadAPIAuthBeforeMethodChecksTestCase(UploadAPIAuthTestCase):
    upload_put_allowed = False
    upload_delete_allowed = False

    @gen_test
    async def test_put_and_delete_without_token_are_unauthorized(self):
        location = self.base_uri + "/" + "a" * 32

        response = await self.async_put(
            location, {"Content-Type": "image/jpeg"}, valid_image()
        )
        self.assert_unauthorized(response)

        response = await self.async_delete(location, {})
        self.assert_unauthorized(response)

    @gen_test
    async def test_put_and_delete_with_token_are_not_allowed(self):
        location = self.base_uri + "/" + "a" * 32
        authorization = {"Authorization": f"Bearer {UPLOAD_TOKEN}"}

        response = await self.async_put(
            location,
            {"Content-Type": "image/jpeg", **authorization},
            valid_image(),
        )
        assert response.code == 405

        response = await self.async_delete(location, authorization)
        assert response.code == 405


class UploadAPIAuthWithKeyfileTestCase(UploadAPIAuthTestCase):
    def get_server(self):
        keyfile = join(self.root_path, "thumbor.key")
        with open(keyfile, "w", encoding="utf-8") as keyfile_handle:
            keyfile_handle.write("keyfile-security-key")
        return ServerParameters(
            8888, "localhost", "thumbor.conf", keyfile, "info", None
        )

    @gen_test
    async def test_keyfile_security_key_is_not_a_token(self):
        assert self.context.server.security_key == b"keyfile-security-key"

        for authorization in (
            "keyfile-security-key",
            "Bearer keyfile-security-key",
            "MY_SECURE_KEY",
            "Bearer MY_SECURE_KEY",
        ):
            with self.subTest(authorization=authorization):
                response = await self.post_image(authorization)

                assert response.code == 401

        response = await self.post_image(f"Bearer {UPLOAD_TOKEN}")
        assert response.code == 201


class UploadAPIAuthWithoutValidTokensTestCase(UploadAPIAuthTestCase):
    upload_auth_tokens = ("", "tok\u00e9n", "with space")

    @gen_test
    async def test_invalid_configured_tokens_reject_every_request(self):
        files_before = self.stored_files()

        for authorization in (
            None,
            "Bearer ",
            "Bearer tok\u00e9n",
            "Bearer with space",
            "Bearer with",
        ):
            with self.subTest(authorization=authorization):
                response = await self.post_image(authorization)

                assert response.code == 401

        assert self.stored_files() == files_before


class UploadAPIAuthDisabledTestCase(UploadAPIAuthTestCase):
    def get_context(self):
        context = super().get_context()
        context.config.UPLOAD_AUTH_REQUIRED = False
        return context

    @gen_test
    async def test_post_without_token_when_auth_is_disabled(self):
        response = await self.post_image()

        assert response.code == 201
        assert "WWW-Authenticate" not in response.headers
