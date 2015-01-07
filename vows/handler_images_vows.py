#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname, exists
from shutil import rmtree
from urllib import quote
import tempfile

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine as PILEngine
from thumbor.storages.file_storage import Storage as FileStorage
from thumbor.utils import which

storage_path = abspath(join(dirname(__file__), 'fixtures/'))

FILE_STORAGE_ROOT_PATH = '/tmp/thumbor-vows/handler_image_vows'


class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)


@Vows.batch
class GetImage(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = FILE_STORAGE_ROOT_PATH
        if exists(FILE_STORAGE_ROOT_PATH):
            rmtree(FILE_STORAGE_ROOT_PATH)

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithUnicodeImage(BaseContext):
        def topic(self):
            response = self.get(u'/unsafe/%s' % quote(u'15967251_212831_19242645_АгатавЗоопарке.jpg'.encode('utf-8')))
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithSignedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class without_unsafe_url_image(TornadoHTTPContext):
        def topic(self):
            response = self.get('/alabama1_ap620%C3%A9.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

    class without_image(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)

    class with_UTF8_URLEncoded_image_name_using_encoded_url(TornadoHTTPContext):
        def topic(self):
            url = '/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg'
            response = self.get(url)
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class with_UTF8_URLEncoded_image_name_using_unsafe(TornadoHTTPContext):
        def topic(self):
            response = self.get(u'/unsafe/smart/alabama1_ap620%C3%A9.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class with_spaces_on_url(TornadoHTTPContext):
        def topic(self):
            response = self.get(u'/unsafe/image%20space.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class with_filter(TornadoHTTPContext):
        def topic(self):
            response = self.get('/5YRxzS2yxZxj9SZ50SoZ11eIdDI=/filters:fill(blue)/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithInvalidQuantizationTableJPEG(BaseContext):
        def topic(self):
            response = self.get('/unsafe/invalid_quantization.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)


@Vows.batch
class GetImageWithoutUnsafe(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.ALLOW_UNSAFE_URL = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithSignedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/unsafe/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)


@Vows.batch
class GetImageWithOLDFormat(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.ALLOW_OLD_URLS = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8890, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application

    class WithEncryptedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/J4ZFjCICZSwwIKfEKNldBNjcG145LDiD2z-4RlOa5ZG4ZY_-8KoEyDOBDfqDBljH/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithBadEncryptedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/27m-vYMKohY6nvEt_D3Zwo7apVq63MS8TP-m1j3BXPGTftnrReTOEoScq1xMXe7h/alabama1_ap620é.jpg')
            return (response.code, response.headers)

        def should_be_404(self, response):
            code, _ = response
            expect(code).to_equal(404)


@Vows.batch
class GetImageWithStoredKeys(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='MYKEY')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.ALLOW_OLD_URLS = True
        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8891, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'MYKEY'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        storage = FileStorage(Context(config=cfg, server=server))

        # Store fixtures (image.jpg and image.txt) into the file storage
        storage.put('image.jpg', open(join(storage_path, 'image.jpg')).read())
        storage.put_crypto('image.jpg')   # Write a file on the file storage containing the security key

        return application

    class WithEncryptedRegularImage(TornadoHTTPContext):
        def topic(self):
            response = self.get('/nty7gpBIRJ3GWtYDLLw6q1PgqTo=/smart/image.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)


@Vows.batch
class GetImageWithAutoWebP(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        self.engine = PILEngine(ctx)

        return application

    class CanConvertJPEG(BaseContext):
        def topic(self):
            return self.get('/unsafe/image.jpg', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })

        def should_be_webp(self, response):
            expect(response.code).to_equal(200)
            expect(response.headers).to_include('Vary')
            expect(response.headers['Vary']).to_include('Accept')

            image = self.engine.create_image(response.body)
            expect(image.format.lower()).to_equal('webp')

    class ShouldNotConvertWebPImage(BaseContext):
        def topic(self):
            return self.get('/unsafe/image.webp', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })

        def should_not_have_vary(self, response):
            expect(response.code).to_equal(200)
            expect(response.headers).not_to_include('Vary')
            image = self.engine.create_image(response.body)
            expect(image.format.lower()).to_equal('webp')

    class ShouldNotConvertAnimatedGif(BaseContext):
        def topic(self):
            return self.get('/unsafe/animated_image.gif', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })

        def should_not_be_webp(self, response):
            expect(response.code).to_equal(200)
            expect(response.headers).not_to_include('Vary')

            image = self.engine.create_image(response.body)
            expect(image.format.lower()).to_equal('gif')

    class WithImageWithSmallWidthAndNoHeight(BaseContext):
        def topic(self):
            response = self.get('/unsafe/0x0:1681x596/1x/hidrocarbonetos_9.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithMonochromaticJPEG(BaseContext):
        def topic(self):
            response = self.get('/unsafe/wellsford.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithCMYK_JPEG(BaseContext):
        def topic(self):
            response = self.get('/unsafe/merrit.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithCMYK_JPEG_AsPNG(BaseContext):
        def topic(self):
            response = self.get('/unsafe/filters:format(png)/merrit.jpg')
            return (response.code, response.headers)

        def should_be_200(self, response):
            code, _ = response
            expect(code).to_equal(200)

    class WithCMYK_JPEG_AsPNG_AcceptingWEBP(BaseContext):
        def topic(self):
            response = self.get('/unsafe/filters:format(png)/merrit.jpg', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })
            return response

        def should_be_200(self, response):
            expect(response.code).to_equal(200)
            image = self.engine.create_image(response.body)
            expect(image.format.lower()).to_equal('png')

    class WithJPEG_AsGIF_AcceptingWEBP(BaseContext):
        def topic(self):
            response = self.get('/unsafe/filters:format(gif)/image.jpg', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })
            return response

        def should_be_200(self, response):
            expect(response.code).to_equal(200)
            image = self.engine.create_image(response.body)
            expect(image.format.lower()).to_equal('gif')

    class HasEtags(BaseContext):
        def topic(self):
            return self.get('/unsafe/image.jpg', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })

        def should_have_etag(self, response):
            expect(response.headers).to_include('Etag')


@Vows.batch
class GetImageWithoutEtags(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.ENABLE_ETAGS = False

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        self.engine = PILEngine(ctx)

        return application

    class CanDisableEtag(BaseContext):
        def topic(self):
            return self.get('/unsafe/image.jpg', headers={
                "Accept": 'image/webp,*/*;q=0.8'
            })

        def should_not_have_etag(self, response):
            expect(response.headers).not_to_include('Etag')


@Vows.batch
class GetImageWithGIFV(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.OPTIMIZERS = [
            'thumbor.optimizers.gifv',
        ]

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        self.engine = PILEngine(ctx)

        return application

    class ShouldConvertAnimatedGifToMp4WhenFilter(BaseContext):
        def topic(self):
            return self.get('/unsafe/filters:gifv()/animated_image.gif')

        def should_be_mp4(self, response):
            expect(response.code).to_equal(200)
            expect(response.headers['Content-Type']).to_equal('video/mp4')

    class ShouldConvertAnimatedGifToWebmWhenFilter(BaseContext):
        def topic(self):
            return self.get('/unsafe/filters:gifv(webm)/animated_image.gif')

        def should_be_mp4(self, response):
            expect(response.code).to_equal(200)
            expect(response.headers['Content-Type']).to_equal('video/webm')


@Vows.batch
class GetImageResultStorage(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.RESULT_STORAGE = 'thumbor.result_storages.file_storage'
        cfg.RESULT_STORAGE_EXPIRATION_SECONDS = 60
        cfg.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = tempfile.mkdtemp(prefix='thumbor_test')
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
        application = ThumborServiceApp(ctx)

        self.engine = PILEngine(ctx)

        return application

    class ShouldLoadGifFromResultStorage(BaseContext):
        def topic(self):
            self.get('/P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')  # Add to result Storage
            return self.get('/P_leK0uires4J3AXg5RkKfSWH4A=/animated_image.gif')

        def should_ok(self, response):
            expect(response.code).to_equal(200)

    class ShouldLoadGifVFromResultStorage(BaseContext):
        def topic(self):
            self.get('/degWAAUDokT-7K81r2BXoPTbg8c=/filters:gifv()/animated_image.gif')  # Add to result Storage
            return self.get('/degWAAUDokT-7K81r2BXoPTbg8c=/filters:gifv()/animated_image.gif')

        def should_ok(self, response):
            expect(response.code).to_equal(200)
