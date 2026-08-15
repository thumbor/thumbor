# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re
from pathlib import Path
from tempfile import TemporaryDirectory
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
        assert getattr(params, "_security_key") == b"SECURITY_KEY_FILE"
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
        with pytest.raises(ValueError, match=re.escape(expected_msg)):
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

    @staticmethod
    def test_cant_load_relative_security_key_outside_working_directory():
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            working_directory = temporary_path / "working-directory"
            working_directory.mkdir()
            (temporary_path / "thumbor.key").write_text(
                "SECURITY_KEY_FILE", encoding="utf-8"
            )

            expected_msg = (
                "Security key file path ../thumbor.key resolves outside "
                "its allowed directory. Please verify the keypath argument."
            )

            with mock.patch(
                "thumbor.context.Path.cwd", return_value=working_directory
            ):
                with pytest.raises(ValueError) as error:
                    ServerParameters(
                        port=8888,
                        ip="0.0.0.0",
                        config_path="/my/config_path.conf",
                        keyfile="../thumbor.key",
                        log_level="debug",
                        app_class="app",
                        fd="fd",
                        gifsicle_path="gifsicle_path",
                    )

            assert str(error.value) == expected_msg

    @staticmethod
    def test_can_load_absolute_security_key_outside_working_directory():
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            working_directory = temporary_path / "working-directory"
            working_directory.mkdir()
            keyfile = temporary_path / "thumbor.key"
            keyfile.write_text("SECURITY_KEY_FILE", encoding="utf-8")

            with mock.patch(
                "thumbor.context.Path.cwd", return_value=working_directory
            ):
                params = ServerParameters(
                    port=8888,
                    ip="0.0.0.0",
                    config_path="/my/config_path.conf",
                    keyfile=str(keyfile),
                    log_level="debug",
                    app_class="app",
                    fd="fd",
                    gifsicle_path="gifsicle_path",
                )

            assert params.security_key == b"SECURITY_KEY_FILE"

    @staticmethod
    def test_cant_load_absolute_security_key_symlink_outside_its_directory():
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            allowed_directory = temporary_path / "keys"
            allowed_directory.mkdir()
            keyfile = temporary_path / "thumbor.key"
            keyfile.write_text("SECURITY_KEY_FILE", encoding="utf-8")
            keyfile_symlink = allowed_directory / "thumbor.key"
            keyfile_symlink.symlink_to(keyfile)

            expected_msg = (
                f"Security key file path {keyfile_symlink} resolves outside "
                "its allowed directory. Please verify the keypath argument."
            )

            with pytest.raises(ValueError) as error:
                ServerParameters(
                    port=8888,
                    ip="0.0.0.0",
                    config_path="/my/config_path.conf",
                    keyfile=str(keyfile_symlink),
                    log_level="debug",
                    app_class="app",
                    fd="fd",
                    gifsicle_path="gifsicle_path",
                )

            assert str(error.value) == expected_msg


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
        assert params.accepts_avif is False
        assert params.accepts_heif is False
        assert params.accepts_png is False
        assert params.accepts_jpeg is False
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
        request = mock.Mock(
            path="/test.jpg",
            headers={
                "Accept": "image/webp,image/avif,image/heif,image/png,image/jpeg"
            },
        )
        params = RequestParameters(request=request, image="/test.jpg")
        assert params.accepts_webp is True
        assert params.accepts_avif is True
        assert params.accepts_heif is True
        assert params.accepts_png is True
        assert params.accepts_jpeg is True
        assert params.image_url == "/test.jpg"

    @staticmethod
    def test_accept_header_respects_quality_and_is_case_insensitive():
        request = mock.Mock(
            path="/test.jpg",
            headers={
                "Accept": "IMAGE/AVIF;Q=0, IMAGE/WEBP;Q=0.8, image/png;q=0"
            },
        )

        params = RequestParameters(request=request)

        assert params.accepts_avif is False
        assert params.accepts_webp is True
        assert params.accepts_png is False

    @staticmethod
    def test_explicit_jpeg_rejection_overrides_accept_any():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "image/jpeg;q=0,*/*;q=0.8"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_jpeg is False

    @staticmethod
    def test_accept_any_keeps_legacy_jpeg_support():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "*/*;q=0.8"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_jpeg is True
        assert params.accepts_webp is False

    @staticmethod
    def test_image_wildcard_accepts_image_formats():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "image/*;q=0.8"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_webp is True
        assert params.accepts_avif is True
        assert params.accepts_heif is True
        assert params.accepts_png is True
        assert params.accepts_jpeg is True

    @staticmethod
    def test_image_wildcard_rejection_overrides_accept_any():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "image/*;q=0,*/*;q=0.8"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_webp is False
        assert params.accepts_avif is False
        assert params.accepts_heif is False
        assert params.accepts_png is False
        assert params.accepts_jpeg is False

    @staticmethod
    def test_accept_header_parses_quoted_delimiters_before_quality():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": 'image/webp;profile="a,b;c";q=0,image/jpeg'},
        )

        params = RequestParameters(request=request)

        assert params.accepts_webp is False
        assert params.accepts_jpeg is True

    @staticmethod
    def test_unparameterized_media_range_controls_default_representation():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "image/webp;profile=foo;q=1,image/webp;q=0"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_webp is False

    @staticmethod
    def test_canonical_jpeg_rejection_takes_precedence_over_jpg_alias():
        request = mock.Mock(
            path="/test.jpg",
            headers={"Accept": "image/jpeg;q=0,image/jpg;q=1"},
        )

        params = RequestParameters(request=request)

        assert params.accepts_jpeg is False

    @staticmethod
    def test_preserves_legacy_positional_arguments():
        request = mock.Mock(
            path="/legacy.jpg",
            headers={"Accept": "image/webp"},
        )
        legacy_positional_arguments = [None] * 32
        legacy_positional_arguments[28:] = [True, request, 3600, False]

        params = RequestParameters(*legacy_positional_arguments)

        assert params.url == "/legacy.jpg"
        assert params.accepts_webp is True
        assert params.max_age == 3600
        assert params.auto_png_to_jpg is False


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

        assert ctx_importer.engine.__class__ == importer.engine
        assert ctx_importer.gif_engine.__class__ == importer.gif_engine

        assert ctx_importer.storage.__class__ == importer.storage
        assert ctx_importer.result_storage.__class__ == importer.result_storage
        assert (
            ctx_importer.upload_photo_storage.__class__
            == importer.upload_photo_storage
        )

        assert ctx_importer.loader == importer.loader
        assert ctx_importer.detectors == importer.detectors
        assert ctx_importer.filters == importer.filters
        assert ctx_importer.optimizers == importer.optimizers
        assert ctx_importer.url_signer == importer.url_signer
