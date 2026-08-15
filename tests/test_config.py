# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import expanduser
from unittest import TestCase, mock

from thumbor.config import Config, format_value, generate_config


class ConfigTestCase(TestCase):
    @mock.patch("derpconf.config.generate_config")
    def test_can_generate_config(self, config_mock):
        generate_config()
        assert config_mock.called

    def test_can_format_value(self):
        assert format_value("qwe") == "'qwe'"
        assert format_value(["qwe", "rty"]) == "[\n#    qwe#    rty#]"
        assert format_value(230) == 230


class ConfigValuesTestCase(TestCase):
    def get_default_storage(self):
        return "thumbor.storages.file_storage"

    def get_config(self):
        return (
            ("MAX_WIDTH", 0),
            ("MAX_HEIGHT", 0),
            ("ALLOWED_SOURCES", []),
            ("QUALITY", 80),
            ("LOADER", "thumbor.loaders.http_loader"),
            ("STORAGE", self.get_default_storage()),
            ("ENGINE", "thumbor.engines.pil"),
            ("GIF_ENGINE", "thumbor.engines.gif"),
            ("URL_SIGNER", "libthumbor.url_signers.base64_hmac_sha1"),
            ("ALLOW_UNSAFE_URL", True),
            ("FILE_LOADER_ROOT_PATH", expanduser("~")),
            ("STORAGE_EXPIRATION_SECONDS", 60 * 60 * 24 * 30),
            ("STORES_CRYPTO_KEY_FOR_EACH_IMAGE", False),
            ("MIXED_STORAGE_FILE_STORAGE", "thumbor.storages.no_storage"),
            ("MIXED_STORAGE_CRYPTO_STORAGE", "thumbor.storages.no_storage"),
            ("MIXED_STORAGE_DETECTOR_STORAGE", "thumbor.storages.no_storage"),
            ("DETECTORS", []),
            ("FACE_DETECTOR_CASCADE_FILE", "haarcascade_frontalface_alt.xml"),
            (
                "FILTERS",
                [
                    "thumbor.filters.brightness",
                    "thumbor.filters.colorize",
                    "thumbor.filters.contrast",
                    "thumbor.filters.rgb",
                    "thumbor.filters.round_corner",
                    "thumbor.filters.quality",
                    "thumbor.filters.noise",
                    "thumbor.filters.watermark",
                    "thumbor.filters.equalize",
                    "thumbor.filters.fill",
                    "thumbor.filters.sharpen",
                    "thumbor.filters.strip_exif",
                    "thumbor.filters.strip_icc",
                    "thumbor.filters.frame",
                    "thumbor.filters.grayscale",
                    "thumbor.filters.rotate",
                    "thumbor.filters.format",
                    "thumbor.filters.max_bytes",
                    "thumbor.filters.convolution",
                    "thumbor.filters.blur",
                    "thumbor.filters.extract_focal",
                    "thumbor.filters.focal",
                    "thumbor.filters.no_upscale",
                    "thumbor.filters.saturation",
                    "thumbor.filters.max_age",
                    "thumbor.filters.curve",
                    "thumbor.filters.background_color",
                    "thumbor.filters.upscale",
                    "thumbor.filters.proportion",
                    "thumbor.filters.stretch",
                ],
            ),
        )

    def test_default_values(self):
        cfg = Config()
        for key, default_value in self.get_config():
            config_value = getattr(cfg, key)
            assert config_value is not None
            assert config_value == default_value

    def test_config_is_an_alias(self):
        Config.alias("OTHER_ENGINE", "ENGINE")
        cfg = Config(OTHER_ENGINE="x")
        assert cfg.ENGINE == "x"
        assert cfg.OTHER_ENGINE == "x"

    def test_config_is_an_aliased_key(self):
        Config.alias("LOADER_ALIAS", "LOADER")
        cfg = Config(LOADER="y")
        assert cfg.LOADER == "y"
        assert cfg.LOADER_ALIAS == "y"

    def test_with_aliased_aliases(self):
        Config.alias("STORAGE_ALIAS", "STORAGE")
        Config.alias("STORAGE_ALIAS_ALIAS", "STORAGE_ALIAS")
        cfg = Config(STORAGE_ALIAS_ALIAS="z")
        assert cfg.STORAGE == "z"
        assert cfg.STORAGE_ALIAS == "z"
        assert cfg.STORAGE_ALIAS_ALIAS == "z"

    def test_with_aliased_aliases_with_default_values(self):
        Config.alias("STORAGE_ALIAS", "STORAGE")
        Config.alias("STORAGE_ALIAS_ALIAS", "STORAGE_ALIAS")
        cfg = Config()
        assert cfg.STORAGE == self.get_default_storage()
        assert cfg.STORAGE_ALIAS == self.get_default_storage()
        assert cfg.STORAGE_ALIAS_ALIAS == self.get_default_storage()
        assert cfg.__class__.__module__ == "derpconf.config"
