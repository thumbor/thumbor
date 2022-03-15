import os.path
from shutil import which

from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class EngineCase(AsyncHTTPTestCase):
    def get_app(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        server_params = ServerParameters(None, None, None, None, None, None)
        server_params.gifsicle_path = which("gifsicle")

        cfg.DETECTORS = [
            "thumbor.detectors.face_detector",
            "thumbor.detectors.profile_detector",
            "thumbor.detectors.glasses_detector",
            "thumbor.detectors.feature_detector",
        ]
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = os.path.join(
            os.path.dirname(__file__), "imgs"
        )
        cfg.ENGINE = getattr(self, "engine", None)
        cfg.USE_GIFSICLE_ENGINE = True
        cfg.FFMPEG_PATH = which("ffmpeg")
        cfg.ENGINE_THREADPOOL_SIZE = 10
        cfg.OPTIMIZERS = [
            "thumbor.optimizers.gifv",
        ]
        if not cfg.ENGINE:
            return None

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(server_params, cfg, importer)
        application = ThumborServiceApp(ctx)

        return application
