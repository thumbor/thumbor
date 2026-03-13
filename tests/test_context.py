# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase, mock

import pytest

from thumbor.config import Config
from thumbor.context import (
    Context,
    ContextImporter,
    RequestParameters,
    ServerParameters,
    ThreadPool,
)
from thumbor.filters import FiltersFactory
from thumbor.importer import Importer
from thumbor.metrics.logger_metrics import Metrics


class ContextTestCase(TestCase):
    @staticmethod
    def test_can_create_context():
        ctx = Context()

        assert ctx.server is None
        assert ctx.config is None
        assert ctx.modules is None

        assert ctx.metrics is not None
        assert isinstance(ctx.metrics, Metrics)

        assert isinstance(ctx.filters_factory, FiltersFactory)
        assert not ctx.filters_factory.filter_classes_map
        assert ctx.request_handler is None
        assert isinstance(ctx.thread_pool, ThreadPool)
        assert isinstance(ctx.headers, dict)
        assert not ctx.headers

    @staticmethod
    def test_can_create_context_with_importer():
        cfg = Config()
        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(config=cfg, importer=importer)

        assert ctx.modules is not None
        assert ctx.modules.importer == importer

    @staticmethod
    def test_can_create_context_without_importer_metrics():
        cfg = Config(
            METRICS="",
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer)

        assert ctx.modules is not None
        assert ctx.modules.importer == importer

    @staticmethod
    def test_can_config_define_app_class():
        server = ServerParameters(
            port=8888,
            ip="0.0.0.0",
            config_path="/my/config_path.conf",
            keyfile="./tests/fixtures/thumbor.key",
            log_level="debug",
            app_class="thumbor.app.ThumborServiceApp",
        )

        cfg = Config(
            APP_CLASS="config.app",
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer, server=server)

        assert ctx.app_class == "config.app"

    @staticmethod
    def test_can_server_app_class_override_config():
        server = ServerParameters(
            port=8888,
            ip="0.0.0.0",
            config_path="/my/config_path.conf",
            keyfile="./tests/fixtures/thumbor.key",
            log_level="debug",
            app_class="server.app",
        )

        cfg = Config(
            APP_CLASS="config.app",
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer, server=server)

        assert ctx.app_class == "server.app"


class ServerParametersTestCase(TestCase):
    @staticmethod
    def test_can_create_server_parameters():
        params = ServerParameters(
            port=8888,
            ip="0.0.0.0",
            config_path="/my/config_path.conf",
            keyfile="./tests/fixtures/thumbor.key",
            log_level="debug",
            app_class="app",
            fd="fd",
            gifsicle_path="gifsicle_path",
        )

        assert params.port == 8888
        assert params.ip == "0.0.0.0"
        assert params.config_path == "/my/config_path.conf"
        assert params.keyfile == "./tests/fixtures/thumbor.key"
        assert params.log_level == "debug"
        assert params.app_class == "app"
        assert params.security_key == b"SECURITY_KEY_FILE"
        assert params.fd == "fd"
        assert params.gifsicle_path == "gifsicle_path"

        assert params.security_key == b"SECURITY_KEY_FILE"

    @staticmethod
    def test_can_set_security_key():
        params = ServerParameters(
            port=8888,
            ip="0.0.0.0",
            config_path="/my/config_path.conf",
            keyfile="./tests/fixtures/thumbor.key",
            log_level="debug",
            app_class="app",
            fd="fd",
            gifsicle_path="gifsicle_path",
        )

        params.security_key = "testé"
        assert params.security_key == "testé"

    @staticmethod
    def test_loading_does_nothing_if_no_keyfile():
        params = ServerParameters(
            port=8888,
            ip="0.0.0.0",
            config_path="/my/config_path.conf",
            keyfile=None,
            log_level="debug",
            app_class="app",
            fd="fd",
            gifsicle_path="gifsicle_path",
        )
        assert params.security_key is None

    @staticmethod
    def test_cant_load_invalid_security_key_file():
        expected_msg = (
            "Could not find security key file at /bogus."
            " Please verify the keypath argument."
        )
        with pytest.raises(ValueError, match=expected_msg):
            ServerParameters(
                port=8888,
                ip="0.0.0.0",
                config_path="/my/config_path.conf",
                keyfile="/bogus",
                log_level="debug",
                app_class="app",
                fd="fd",
                gifsicle_path="gifsicle_path",
            )


class RequestParametersTestCase(TestCase):
    @staticmethod
    def test_can_create_request_parameters():
        params = RequestParameters()

        assert params.debug is False
        assert params.meta is False
        assert params.trim is None
        assert params.crop == {"top": 0, "right": 0, "bottom": 0, "left": 0}
        assert params.should_crop is False

        assert params.adaptive is False
        assert params.full is False
        assert params.fit_in is False
        assert params.stretch is False

        assert params.width == 0
        assert params.height == 0

        assert params.horizontal_flip is False
        assert params.vertical_flip is False

        assert params.halign == "center"
        assert params.valign == "middle"

        assert params.smart is False

        assert params.filters == []
        assert params.image_url is None
        assert params.url is None
        assert params.detection_error is None
        assert params.quality == 80
        assert params.buffer is None

        assert params.focal_points == []

        assert params.hash is None
        assert params.prevent_result_storage is False
        assert params.unsafe is False
        assert params.format is None
        assert params.accepts_webp is False
        assert params.max_bytes is None
        assert params.max_age is None

    @staticmethod
    def test_can_get_params_with_trim():
        params = RequestParameters(trim="trim")
        assert params.trim_pos == "top-left"
        assert params.trim_tolerance == 0

    @staticmethod
    def test_can_get_params_with_trim_with_custom_pos():
        params = RequestParameters(trim="trim:bottom-right:10")
        assert params.trim_pos == "bottom-right"
        assert params.trim_tolerance == 10

    @staticmethod
    def test_can_get_params_with_crop():
        params = RequestParameters(
            crop_left=10,
            crop_right=20,
            crop_top=30,
            crop_bottom=40,
        )
        assert params.crop == {
            "top": 30,
            "right": 20,
            "bottom": 40,
            "left": 10,
        }

    @staticmethod
    def test_can_get_params_with_custom_crop():
        params = RequestParameters(
            crop={"top": 30, "right": 20, "bottom": 40, "left": 10}
        )
        assert params.crop == {
            "top": 30,
            "right": 20,
            "bottom": 40,
            "left": 10,
        }
        assert params.should_crop is True

    @staticmethod
    def test_can_get_orig_dimensions():
        params = RequestParameters(
            width="orig",
            height="orig",
        )
        assert params.width == "orig"
        assert params.height == "orig"

    @staticmethod
    def test_can_add_filters():
        params = RequestParameters(filters=["a", "b"])
        assert len(params.filters) == 2

    @staticmethod
    def test_can_add_focal_points():
        params = RequestParameters(focal_points=["a", "b"])
        assert len(params.focal_points) == 2

    @staticmethod
    def test_can_get_params_from_request():
        request = mock.Mock(path="/test.jpg", headers={"Accept": "image/webp"})
        params = RequestParameters(request=request, image="/test.jpg")
        assert params.accepts_webp is True
        assert params.image_url == "/test.jpg"


class ContextImporterTestCase(TestCase):
    @staticmethod
    def test_can_create_context_importer():
        cfg = Config(
            RESULT_STORAGE="thumbor.result_storages.file_storage",
        )
        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(config=cfg, importer=importer)

        ctx_importer = ContextImporter(ctx, importer)
        assert ctx_importer.context == ctx
        assert ctx_importer.importer == importer
        assert isinstance(ctx_importer.engine, importer.engine)
        assert isinstance(ctx_importer.gif_engine, importer.gif_engine)

        assert isinstance(ctx_importer.storage, importer.storage)
        assert isinstance(ctx_importer.result_storage, importer.result_storage)
        assert isinstance(
            ctx_importer.upload_photo_storage, importer.upload_photo_storage
        )

        assert ctx_importer.loader == importer.loader
        assert ctx_importer.detectors == importer.detectors
        assert ctx_importer.filters == importer.filters
        assert ctx_importer.optimizers == importer.optimizers
        assert ctx_importer.url_signer == importer.url_signer
