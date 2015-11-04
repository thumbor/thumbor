#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from urllib import quote
import tempfile
import shutil
from os.path import abspath, join, dirname
import os

import tornado.web
from preggy import expect
from mock import Mock, patch

from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context, ServerParameters
from thumbor.handlers import FetchResult, BaseHandler
from thumbor.utils import which
from tests.base import TestCase, PythonTestCase
from thumbor.engines.pil import Engine
from tests.fixtures.images import (
    default_image,
    alabama1,
    space_image,
    invalid_quantization,
    animated_image,
    not_so_animated_image,
)


class FetchResultTestCase(PythonTestCase):
    def test_can_create_default_fetch_result(self):
        result = FetchResult()
        expect(result.normalized).to_be_false()
        expect(result.buffer).to_be_null()
        expect(result.engine).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.loader_error).to_be_null()

    def test_can_create_fetch_result(self):
        buffer_mock = Mock()
        engine_mock = Mock()
        error_mock = Mock()
        result = FetchResult(
            normalized=True,
            buffer=buffer_mock,
            engine=engine_mock,
            successful=True,
            loader_error=error_mock,
        )
        expect(result.normalized).to_be_true()
        expect(result.buffer).to_equal(buffer_mock)
        expect(result.engine).to_equal(engine_mock)
        expect(result.successful).to_be_true()
        expect(result.loader_error).to_equal(error_mock)


class ErrorHandler(BaseHandler):
    def get(self):
        self._error(403)


class BaseHandlerTestApp(tornado.web.Application):
    def __init__(self, context):
        self.context = context
        super(BaseHandlerTestApp, self).__init__([
            (r'/error', ErrorHandler),
        ])


class BaseHandlerTestCase(TestCase):
    def get_app(self):
        self.context = self.get_context()
        return BaseHandlerTestApp(self.context)

    def test_can_get_an_error(self):
        response = self.fetch('/error')
        expect(response.code).to_equal(403)


class BaseImagingTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kw):
        cls.root_path = tempfile.mkdtemp()
        cls.loader_path = abspath(join(dirname(__file__), '../fixtures/images/'))
        cls.base_uri = "/image"

    @classmethod
    def tearDownClass(cls, *args, **kw):
        shutil.rmtree(cls.root_path)


class ImagingOperationsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return Context(server, cfg, importer)

    def test_can_get_image(self):
        response = self.fetch('/unsafe/smart/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_image_without_extension(self):
        response = self.fetch('/unsafe/smart/image')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_get_unknown_image_returns_not_found(self):
        response = self.fetch('/unsafe/smart/imag')
        expect(response.code).to_equal(404)

    def test_can_get_unicode_image(self):
        response = self.fetch(u'/unsafe/%s' % quote(u'15967251_212831_19242645_АгатавЗоопарке.jpg'.encode('utf-8')))
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_can_get_signed_regular_image(self):
        response = self.fetch('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_url_without_unsafe_or_hash_fails(self):
        response = self.fetch('/alabama1_ap620%C3%A9.jpg')
        expect(response.code).to_equal(400)

    def test_url_without_image(self):
        response = self.fetch('/unsafe/')
        expect(response.code).to_equal(400)

    def test_utf8_encoded_image_name_with_encoded_url(self):
        url = '/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg'
        response = self.fetch(url)
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(alabama1())

    def test_image_with_spaces_on_url(self):
        response = self.fetch(u'/unsafe/image%20space.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(space_image())

    def test_can_get_image_with_filter(self):
        response = self.fetch('/5YRxzS2yxZxj9SZ50SoZ11eIdDI=/filters:fill(blue)/image.jpg')
        expect(response.code).to_equal(200)

    def test_can_get_image_with_invalid_quantization_table(self):
        response = self.fetch('/unsafe/invalid_quantization.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(invalid_quantization())

    def test_getting_invalid_image_returns_bad_request(self):
        response = self.fetch('/unsafe/image_invalid.jpg')
        expect(response.code).to_equal(400)

    def test_can_read_monochromatic_jpeg(self):
        response = self.fetch('/unsafe/wellsford.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    def test_can_read_image_with_small_width_and_no_height(self):
        response = self.fetch('/unsafe/0x0:1681x596/1x/hidrocarbonetos_9.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    def test_can_read_cmyk_jpeg(self):
        response = self.fetch('/unsafe/merrit.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_jpeg()

    def test_can_read_cmyk_jpeg_as_png(self):
        response = self.fetch('/unsafe/filters:format(png)/merrit.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()


class ImageOperationsWithoutUnsafeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return Context(server, cfg, importer)

    def test_can_get_image_with_signed_url(self):
        response = self.fetch('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_getting_unsafe_image_fails(self):
        response = self.fetch('/unsafe/smart/image.jpg')
        expect(response.code).to_equal(400)


class ImageOperationsWithStoredKeysTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='MYKEY')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.ALLOW_OLD_URLS = True
        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True

        cfg.STORAGE = 'thumbor.storages.file_storage'
        cfg.STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8891, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'MYKEY'
        return Context(server, cfg, importer)

    def test_stored_security_key_with_regular_image(self):
        storage = self.context.modules.storage
        self.context.server.security_key = 'MYKEY'
        storage.put_crypto('image.jpg')   # Write a file on the file storage containing the security key
        self.context.server.security_key = 'MYKEY2'

        try:
            response = self.fetch('/nty7gpBIRJ3GWtYDLLw6q1PgqTo=/smart/image.jpg')
            expect(response.code).to_equal(200)
            expect(response.body).to_be_similar_to(default_image())
        finally:
            self.context.server.security_key = 'MYKEY'

    def test_stored_security_key_with_regular_image_with_querystring(self):
        storage = self.context.modules.storage
        self.context.server.security_key = 'MYKEY'
        storage.put_crypto('image.jpg%3Fts%3D1')   # Write a file on the file storage containing the security key
        self.context.server.security_key = 'MYKEY2'

        response = self.fetch('/Iw7LZGdr-hHj2gQ4ZzksP3llQHY=/smart/image.jpg%3Fts%3D1')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())

    def test_stored_security_key_with_regular_image_with_hash(self):
        storage = self.context.modules.storage
        self.context.server.security_key = 'MYKEY'
        storage.put_crypto('image.jpg%23something')   # Write a file on the file storage containing the security key
        self.context.server.security_key = 'MYKEY2'

        response = self.fetch('/fxOHtHcTZMyuAQ1YPKh9KWg7nO8=/smart/image.jpg%23something')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(default_image())


class ImageOperationsWithAutoWebPTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which('gifsicle')
        return ctx

    def get_as_webp(self, url):
        return self.fetch(url, headers={
            "Accept": 'image/webp,*/*;q=0.8'
        })

    def test_can_auto_convert_jpeg(self):
        response = self.get_as_webp('/unsafe/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.headers).to_include('Vary')
        expect(response.headers['Vary']).to_include('Accept')

        expect(response.body).to_be_webp()

    def test_should_not_convert_webp_if_already_webp(self):
        response = self.get_as_webp('/unsafe/image.webp')

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include('Vary')
        expect(response.body).to_be_webp()

    def test_should_not_convert_webp_if_bigger_than_89478485_pixels(self):
        response = self.get_as_webp('/unsafe/16384.png')

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include('Vary')
        expect(response.body).to_be_png()

    def test_should_not_convert_animated_gifs_to_webp(self):
        response = self.get_as_webp('/unsafe/animated_image.gif')

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include('Vary')
        expect(response.body).to_be_gif()

    def test_should_convert_image_with_small_width_and_no_height(self):
        response = self.get_as_webp('/unsafe/0x0:1681x596/1x/hidrocarbonetos_9.jpg')

        expect(response.code).to_equal(200)
        expect(response.body).to_be_webp()

    def test_should_convert_monochromatic_jpeg(self):
        response = self.get_as_webp('/unsafe/wellsford.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_webp()

    def test_should_convert_cmyk_jpeg(self):
        response = self.get_as_webp('/unsafe/merrit.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_webp()

    def test_shouldnt_convert_cmyk_jpeg_if_format_specified(self):
        response = self.get_as_webp('/unsafe/filters:format(png)/merrit.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_png()

    def test_shouldnt_convert_cmyk_jpeg_if_gif(self):
        response = self.get_as_webp('/unsafe/filters:format(gif)/merrit.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_gif()

    def test_shouldnt_convert_cmyk_if_format_specified(self):
        response = self.get_as_webp('/unsafe/filters:format(gif)/image.jpg')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_gif()

    def test_converting_return_etags(self):
        response = self.get_as_webp('/unsafe/image.jpg')
        expect(response.headers).to_include('Etag')


class ImageOperationsWithoutEtagsTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        return Context(server, cfg, importer)

    def test_can_get_image_without_etags(self):
        response = self.fetch('/unsafe/image.jpg', headers={
            "Accept": 'image/webp,*/*;q=0.8'
        })

        expect(response.code).to_equal(200)
        expect(response.headers).not_to_include('Etag')


class ImageOperationsWithGifVTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.FFMPEG_PATH = which('ffmpeg')
        cfg.OPTIMIZERS = [
            'thumbor.optimizers.gifv',
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which('gifsicle')
        return ctx

    def test_should_convert_animated_gif_to_mp4_when_filter_without_params(self):
        response = self.fetch('/unsafe/filters:gifv()/animated_image.gif')

        expect(response.code).to_equal(200)
        expect(response.headers['Content-Type']).to_equal('video/mp4')

    def test_should_convert_animated_gif_to_webm_when_filter_with_gifv_webm_param(self):
        response = self.fetch('/unsafe/filters:gifv(webm)/animated_image.gif')

        expect(response.code).to_equal(200)
        expect(response.headers['Content-Type']).to_equal('video/webm')


class ImageOperationsImageCoverTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.AUTO_WEBP = True
        cfg.USE_GIFSICLE_ENGINE = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which('gifsicle')
        return ctx

    def test_can_get_image_cover(self):
        response = self.fetch('/unsafe/filters:cover()/animated_image.gif')

        expect(response.code).to_equal(200)
        expect(response.headers['Content-Type']).to_equal('image/gif')


class ImageOperationsWithResultStorageTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.FFMPEG_PATH = which('ffmpeg')
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            'thumbor.optimizers.gifv',
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which('gifsicle')

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    @patch('tornado.ioloop.IOLoop.instance')
    def test_saves_image_to_result_storage(self, instance_mock):
        instance_mock.return_value = self.io_loop
        response = self.fetch('/P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')
        expect(response.code).to_equal(200)

        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path('P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')
        expect(expected_path).to_exist()
        expect(response.body).to_be_similar_to(animated_image())


class ImageOperationsResultStorageOnlyTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = '/tmp/path/that/does/not/exist'

        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.FFMPEG_PATH = which('ffmpeg')

        cfg.USE_GIFSICLE_ENGINE = True
        cfg.AUTO_WEBP = True
        cfg.OPTIMIZERS = [
            'thumbor.optimizers.gifv',
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        ctx.server.gifsicle_path = which('gifsicle')

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    def test_loads_image_from_result_storage(self):
        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path('P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')
        os.makedirs(dirname(expected_path))
        with open(expected_path, 'w') as img:
            img.write(animated_image())

        response = self.fetch('/P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(animated_image())


class ImageOperationsWithGifWithoutGifsicle(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)

        return ctx

    def test_should_be_ok_with_single_frame_gif(self):
        response = self.fetch('/HPbIwc4ACNupMwcOQMUnAEy9c_k=/not_so_animated_image.gif')

        expect(response.code).to_equal(200)
        expect(response.headers['Content-Type']).to_equal('image/gif')
        expect(response.body).to_be_similar_to(not_so_animated_image())


class ImageOperationsWithGifWithoutGifsicleOnResultStorage(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = '/tmp/path/that/does/not/exist'

        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path

        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)

        return ctx

    @property
    def result_storage(self):
        return self.context.modules.result_storage

    def test_loads_image_from_result_storage(self):
        self.context.request = Mock(
            accepts_webp=False,
        )
        expected_path = self.result_storage.normalize_path('HPbIwc4ACNupMwcOQMUnAEy9c_k=/not_so_animated_image.gif')
        os.makedirs(dirname(expected_path))
        with open(expected_path, 'w') as img:
            img.write(not_so_animated_image())

        response = self.fetch('/HPbIwc4ACNupMwcOQMUnAEy9c_k=/not_so_animated_image.gif')
        expect(response.code).to_equal(200)
        expect(response.body).to_be_similar_to(not_so_animated_image())


class ImageOperationsWithMaxWidthAndMaxHeight(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path

        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.AUTO_WEBP = True
        cfg.MAX_WIDTH = 150
        cfg.MAX_HEIGHT = 150

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)

        return ctx

    def test_should_be_ok_but_150x150(self):
        response = self.fetch('/unsafe/200x200/wellsford.jpg')
        engine = Engine(self.context)
        engine.load(response.body, '.jpg')
        expect(response.code).to_equal(200)
        expect(response.headers['Content-Type']).to_equal('image/jpeg')
        expect(engine.size).to_equal((150, 150))
