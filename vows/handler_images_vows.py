#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com
from thumbor.storages.file_storage import Storage as FileStorage
from os.path import abspath, join, dirname
import shutil

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.importer import Importer
from thumbor.config import Config
from thumbor.context import Context, ServerParameters

storage_path = abspath(join(dirname(__file__), 'fixtures/'))

class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)

@Vows.batch
class GetImage(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='ACME-SEC')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'ACME-SEC'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application


    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/unsafe/smart/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class WithSignedRegularImage(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class with_UTF8_URLEncoded_image_name(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620%C3%A9.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class without_unsafe_url_image(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/alabama1_ap620%C3%A9.jpg')
            return (rsp.code, rsp.headers)

        def should_be_404(self, (code, _)):
            expect(code).to_equal(404)

    class without_image(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/unsafe/')
            return (rsp.code, rsp.headers)

        def should_be_404(self, (code, _)):
            expect(code).to_equal(404)

    class with_UTF8_URLEncoded_image_name(TornadoHTTPContext):
        def topic(self):
            rsp = self.get(u'/unsafe/smart/alabama1_ap620é.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class with_UTF8_URLEncoded_image_name(TornadoHTTPContext):
        def topic(self):
            rsp = self.get(u'/lc6e3kkm_2Ww7NWho8HPOe-sqLU=/smart/alabama1_ap620é.jpg')
            return (rsp.code, rsp.headers)

        def should_be_404(self, (code, _)):
            expect(code).to_equal(404)

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
            rsp = self.get('/_wIUeSaeHw8dricKG2MGhqu5thk=/smart/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class WithRegularImage(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/unsafe/smart/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_404(self, (code, _)):
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
            rsp = self.get('/J4ZFjCICZSwwIKfEKNldBNjcG145LDiD2z-4RlOa5ZG4ZY_-8KoEyDOBDfqDBljH/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

    class WithBadEncryptedRegularImage(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/27m-vYMKohY6nvEt_D3Zwo7apVq63MS8TP-m1j3BXPGTftnrReTOEoScq1xMXe7h/alabama1_ap620é.jpg')
            return (rsp.code, rsp.headers)

        def should_be_404(self, (code, _)):
            expect(code).to_equal(404)

#        cfg.STORAGE="thumbor.storages.file_storage"
#        cfg.FILE_STORAGE_ROOT_PATH=storage_path
#        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True

@Vows.batch
class GetImageWithStoredKeys(BaseContext):
    def get_app(self):
        cfg = Config(SECURITY_KEY='MYKEY')
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = storage_path
        cfg.ALLOW_UNSAFE_URL = False
        cfg.ALLOW_OLD_URLS = True
        cfg.STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(8891, 'localhost', 'thumbor.conf', None, 'info', None)
        server.security_key = 'MYKEY'
        ctx = Context(server, cfg, importer)
        application = ThumborServiceApp(ctx)

        storage = FileStorage(Context(config=cfg, server=server))

        # Store fixtures (image.jpg and image.txt) into the file storage
        storage.put('image.jpg', file(join(storage_path, 'image.jpg')).read())
        storage.put_crypto('image.jpg')   # Write a file on the file storage containing the security key

        return application

    class WithEncryptedRegularImage(TornadoHTTPContext):
        def topic(self):
            rsp = self.get('/nty7gpBIRJ3GWtYDLLw6q1PgqTo=/smart/image.jpg')
            return (rsp.code, rsp.headers)

        def should_be_200(self, (code, _)):
            expect(code).to_equal(200)

