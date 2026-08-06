# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import hashlib
import tempfile
from datetime import datetime
from os.path import abspath, dirname, exists, join
from unittest import mock
from urllib.parse import unquote

from preggy import expect
from tornado.testing import gen_test

from thumbor.auto_image_format import get_auto_image_format_cache_key
from thumbor.config import Config
from thumbor.context import RequestParameters
from thumbor.result_storages import ResultStorageResult
from thumbor.result_storages.file_storage import Storage as FileStorage
from thumbor.testing import TestCase


class BaseFileStorageTestCase(TestCase):
    def __init__(self, *args, **kw):
        self.storage_path = None
        self.context = None
        self.file_storage = None
        super().__init__(*args, **kw)

    def get_config(self):
        config = super().get_config()
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.storage_path.name
        return config

    def tearDown(self):
        super().tearDown()
        if self.storage_path is not None:
            self.storage_path.cleanup()

    @staticmethod
    def get_request():
        return RequestParameters()

    @staticmethod
    def get_fixture_path():
        return abspath(join(dirname(__file__), "../fixtures/result_storages"))

    @staticmethod
    def get_image_fixture_path(filename):
        return abspath(join(dirname(__file__), "../fixtures/images", filename))

    def read_image_fixture(self, filename):
        with open(self.get_image_fixture_path(filename), "rb") as image_file:
            return image_file.read()

    def get_context(self):
        ctx = super().get_context()
        cfg = self.get_config()
        ctx.config = cfg
        ctx.request = self.get_request()
        self.context = ctx
        self.file_storage = FileStorage(self.context)
        return ctx

    @staticmethod
    def get_http_path():
        return "http://example.com/path/to/a.jpg"

    def put_legacy_fixture(self, filename):
        legacy_path = self.file_storage.normalize_path_legacy(
            self.context.request.url
        )
        self.file_storage.ensure_dir(dirname(legacy_path))

        image_bytes = self.read_image_fixture(filename)

        with open(legacy_path, "wb") as legacy_file:
            legacy_file.write(image_bytes)

        return legacy_path, image_bytes

    def put_previous_hashed_fixture(self, prefix, filename):
        path = self.context.request.url
        # This reproduces the legacy cache layout; SHA-1 is not used for
        # security or integrity checks.
        digest = hashlib.sha1(
            unquote(path).encode("utf-8"), usedforsecurity=False
        ).hexdigest()
        previous_path = join(
            self.storage_path.name,
            prefix,
            digest[:2],
            digest[2:4],
            digest[4:],
        )
        self.file_storage.ensure_dir(dirname(previous_path))

        image_bytes = self.read_image_fixture(filename)

        with open(previous_path, "wb") as previous_file:
            previous_file.write(image_bytes)

        return previous_path, image_bytes


class FileStorageTestCase(BaseFileStorageTestCase):
    def test_is_not_legacy_auto_webp(self):
        expect(self.file_storage.is_auto_webp).to_be_false()

    def test_is_auto_webp_override_controls_legacy_cache_key(self):
        class CustomFileStorage(FileStorage):
            @property
            def is_auto_webp(self):
                return True

        custom_storage = CustomFileStorage(self.context)

        expect(custom_storage.normalize_path(self.get_http_path())).to_equal(
            f"{self.storage_path.name}/auto_webp/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )

    @gen_test
    async def test_normalized_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(
            self.file_storage.normalize_path(self.get_http_path())
        ).to_equal(
            f"{self.storage_path.name}/default/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )

    @gen_test
    async def test_normalized_path_without_request(self):
        del self.context.request

        expect(self.file_storage).not_to_be_null()
        expect(
            self.file_storage.normalize_path(self.get_http_path())
        ).to_equal(
            f"{self.storage_path.name}/default/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )

    @gen_test
    async def test_migrates_legacy_default_cache(self):
        self.context.request.url = self.get_http_path()
        legacy_path, image_bytes = self.put_legacy_fixture("image.jpg")
        current_path = self.file_storage.normalize_path(
            self.context.request.url
        )

        result = await self.file_storage.get()

        expect(result.buffer).to_equal(image_bytes)
        expect(exists(legacy_path)).to_be_false()
        expect(exists(current_path)).to_be_true()


class WebPFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        return Config(
            AUTO_WEBP=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.storage_path.name,
        )

    def tearDown(self):
        super().tearDown()
        self.storage_path.cleanup()

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(accepts_webp=True)

    def test_preserves_legacy_is_auto_webp_property(self):
        expect(self.file_storage.is_auto_webp).to_be_true()

    def test_is_auto_webp_override_can_disable_legacy_cache_key(self):
        class CustomFileStorage(FileStorage):
            @property
            def is_auto_webp(self):
                return False

        custom_storage = CustomFileStorage(self.context)

        expect(custom_storage.normalize_path(self.get_http_path())).to_equal(
            f"{self.storage_path.name}/default/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )

    @gen_test
    async def test_normalized_path_with_auto_webp_path(self):
        expect(self.file_storage).not_to_be_null()
        expect(
            self.file_storage.normalize_path(self.get_http_path())
        ).to_equal(
            f"{self.storage_path.name}/auto_webp/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )

    @gen_test
    async def test_migrates_legacy_auto_webp_cache(self):
        self.context.request.url = self.get_http_path()
        legacy_path, image_bytes = self.put_legacy_fixture("image.webp")
        current_path = self.file_storage.normalize_path(
            self.context.request.url
        )

        result = await self.file_storage.get()

        expect(result.buffer).to_equal(image_bytes)
        expect(exists(legacy_path)).to_be_false()
        expect(exists(current_path)).to_be_true()


class AutoAvifFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        return Config(
            AUTO_AVIF=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.storage_path.name,
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url=self.get_http_path())

    @gen_test
    async def test_does_not_migrate_unsafe_legacy_default_cache(self):
        legacy_path, _ = self.put_legacy_fixture("image.jpg")
        current_path = self.file_storage.normalize_path(
            self.context.request.url
        )

        result = await self.file_storage.get()

        expect(result).to_be_null()
        expect(exists(legacy_path)).to_be_true()
        expect(exists(current_path)).to_be_false()

    def test_uses_isolated_default_namespace(self):
        expect(
            self.file_storage.normalize_path(self.context.request.url)
        ).to_equal(
            f"{self.storage_path.name}/"
            "auto_format_v1_flags_preserve_default/b6/be/"
            "a3e916129541a9e7146f69a15eb4d7c77c98"
        )


class AutoPngToJpgFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        return Config(
            AUTO_PNG_TO_JPG=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.storage_path.name,
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url=self.get_http_path())

    @gen_test
    async def test_does_not_read_previous_default_cache(self):
        previous_path, _ = self.put_previous_hashed_fixture(
            "default", "1x1.png"
        )
        current_path = self.file_storage.normalize_path(
            self.context.request.url
        )

        result = await self.file_storage.get()

        expect(result).to_be_null()
        expect(exists(previous_path)).to_be_true()
        expect(exists(current_path)).to_be_false()


class AutoWebPAndAvifFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        self.storage_path = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        return Config(
            AUTO_WEBP=True,
            AUTO_AVIF=True,
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.storage_path.name,
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url=self.get_http_path(), accepts_webp=True)

    @gen_test
    async def test_does_not_migrate_contaminated_legacy_webp_cache(self):
        legacy_path, _ = self.put_legacy_fixture("image.avif")
        current_path = self.file_storage.normalize_path(
            self.context.request.url
        )

        result = await self.file_storage.get()

        expect(result).to_be_null()
        expect(exists(legacy_path)).to_be_true()
        expect(exists(current_path)).to_be_false()


class AutoImageFormatCacheKeyTestCase(TestCase):
    def test_extended_formats_use_isolated_cache_keys(self):
        config = Config(AUTO_AVIF=True)

        expect(
            get_auto_image_format_cache_key(
                config, RequestParameters(accepts_avif=True)
            )
        ).to_equal("auto_format_v1_flags_preserve_avif")
        expect(
            get_auto_image_format_cache_key(config, RequestParameters())
        ).to_equal("auto_format_v1_flags_preserve_default")

    def test_cache_key_separates_png_to_jpg_fallback(self):
        request = RequestParameters(accepts_heif=True)
        flags_without_fallback = Config(AUTO_HEIF=True, AUTO_PNG_TO_JPG=False)
        flags_with_fallback = Config(AUTO_HEIF=True, AUTO_PNG_TO_JPG=True)

        cache_keys = {
            get_auto_image_format_cache_key(flags_without_fallback, request),
            get_auto_image_format_cache_key(flags_with_fallback, request),
        }

        expect(len(cache_keys)).to_equal(2)

    def test_png_to_jpg_only_uses_isolated_cache_key(self):
        expect(
            get_auto_image_format_cache_key(
                Config(AUTO_PNG_TO_JPG=True), RequestParameters()
            )
        ).to_equal("auto_format_v1_flags_png_to_jpg_default")

    def test_quality_zero_does_not_enter_legacy_webp_cache(self):
        request = mock.Mock(
            path="http://example.com/path/to/a.jpg",
            headers={"Accept": "image/webp;q=0"},
        )

        expect(
            get_auto_image_format_cache_key(
                Config(AUTO_WEBP=True),
                RequestParameters(request=request),
            )
        ).to_be_null()


class ResultStorageResultTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path()
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url="image.jpg")

    @gen_test
    async def test_can_get_image_from_storage(self):
        result = await self.file_storage.get()

        expect(result).to_be_instance_of(ResultStorageResult)
        expect(result.successful).to_equal(True)
        expect(len(result)).to_equal(5319)
        expect(len(result)).to_equal(result.metadata["ContentLength"])
        expect(result.last_modified).to_be_instance_of(datetime)


class ExpiredFileStorageTestCase(BaseFileStorageTestCase):
    def get_config(self):
        return Config(
            RESULT_STORAGE_FILE_STORAGE_ROOT_PATH=self.get_fixture_path(),
            RESULT_STORAGE_EXPIRATION_SECONDS=10,
        )

    def get_request(self):  # pylint: disable=arguments-differ
        return RequestParameters(url="image.jpg")

    @gen_test
    async def test_cannot_get_expired_1_day_old_image(self):
        current_timestamp = (
            datetime.utcnow() - datetime(1970, 1, 1)
        ).total_seconds()
        new_mtime = current_timestamp - 60 * 60 * 24
        with mock.patch(
            "thumbor.result_storages.file_storage.getmtime",
            return_value=new_mtime,
        ):
            result = await self.file_storage.get()
        expect(result).to_be_null()
