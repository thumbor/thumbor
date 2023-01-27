from unittest.mock import patch

from preggy import expect
from tornado.testing import gen_test

from tests.fixtures.images import default_image
from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.engines.pil import Engine
from thumbor.importer import Importer
from thumbor.loaders import LoaderResult


class BaseHandlerLoadingNormalizeImagesTestCase(BaseImagingTestCase):
    def setUp(self):
        super().setUp()
        self.storage_patcher = patch(
            "thumbor.storages.file_storage.Storage.get"
        )
        self.storage_mock = self.storage_patcher.start()
        self.loader_patcher = patch("thumbor.loaders.http_loader.load")
        self.loader_mock = self.loader_patcher.start()

    def tearDown(self):
        super().tearDown()
        self.storage_patcher.stop()
        self.loader_patcher.stop()

    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.loader_path
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.AUTO_WEBP = True

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        ctx = Context(server, cfg, importer)
        return ctx

    @gen_test
    async def test_can_normalize_image_loaded_from_storage(self):
        self.storage_mock.return_value = default_image()
        self.context.config.MAX_HEIGHT = 1
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        expect(response.code).to_equal(200)

        engine = Engine(self.context)
        engine.load(response.body, None)
        expect(engine.size).to_equal((1, 1))

    @gen_test
    async def test_can_normalize_image_loaded_from_upstream(self):
        self.storage_mock.return_value = None
        self.loader_mock.return_value = LoaderResult(buffer=default_image())
        self.context.config.MAX_HEIGHT = 1
        response = await self.async_fetch("/unsafe/smart/image.jpg")
        expect(response.code).to_equal(200)

        engine = Engine(self.context)
        engine.load(response.body, None)
        expect(engine.size).to_equal((1, 1))
