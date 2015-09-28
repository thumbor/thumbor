#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.config import Config

STORAGE_DEFAULT_VALUE = 'thumbor.storages.file_storage'

TEST_DATA = (
    ('MAX_WIDTH', 0),
    ('MAX_HEIGHT', 0),
    ('ALLOWED_SOURCES', []),
    ('QUALITY', 80),
    ('LOADER', 'thumbor.loaders.http_loader'),
    ('STORAGE', STORAGE_DEFAULT_VALUE),
    ('ENGINE', 'thumbor.engines.pil'),
    ('GIF_ENGINE', 'thumbor.engines.gif'),
    ('URL_SIGNER', 'thumbor.url_signers.base64_hmac_sha1'),
    ('ALLOW_UNSAFE_URL', True),
    ('FILE_LOADER_ROOT_PATH', '/tmp'),
    ('STORAGE_EXPIRATION_SECONDS', 60 * 60 * 24 * 30),
    ('STORES_CRYPTO_KEY_FOR_EACH_IMAGE', False),
    ('MONGO_STORAGE_SERVER_HOST', 'localhost'),
    ('MONGO_STORAGE_SERVER_PORT', 27017),
    ('MONGO_STORAGE_SERVER_DB', 'thumbor'),
    ('MONGO_STORAGE_SERVER_COLLECTION', 'images'),
    ('REDIS_STORAGE_SERVER_HOST', 'localhost'),
    ('REDIS_STORAGE_SERVER_PORT', 6379),
    ('REDIS_STORAGE_SERVER_DB', 0),
    ('REDIS_STORAGE_IGNORE_ERRORS', False),
    ('MIXED_STORAGE_FILE_STORAGE', 'thumbor.storages.no_storage'),
    ('MIXED_STORAGE_CRYPTO_STORAGE', 'thumbor.storages.no_storage'),
    ('MIXED_STORAGE_DETECTOR_STORAGE', 'thumbor.storages.no_storage'),
    ('DETECTORS', []),
    ('FACE_DETECTOR_CASCADE_FILE', 'haarcascade_frontalface_alt.xml'),
    ('FILTERS', [
        'thumbor.filters.brightness',
        'thumbor.filters.colorize',
        'thumbor.filters.contrast',
        'thumbor.filters.rgb',
        'thumbor.filters.round_corner',
        'thumbor.filters.quality',
        'thumbor.filters.noise',
        'thumbor.filters.watermark',
        'thumbor.filters.equalize',
        'thumbor.filters.fill',
        'thumbor.filters.sharpen',
        'thumbor.filters.strip_icc',
        'thumbor.filters.frame',
        'thumbor.filters.grayscale',
        'thumbor.filters.rotate',
        'thumbor.filters.format',
        'thumbor.filters.max_bytes',
        'thumbor.filters.convolution',
        'thumbor.filters.blur',
        'thumbor.filters.extract_focal',
        'thumbor.filters.no_upscale',
        'thumbor.filters.saturation',
        'thumbor.filters.max_age',
        'thumbor.filters.curve',
    ])
)


@Vows.batch
class Configuration(Vows.Context):

    class DefaultThumborConf(Vows.Context):
        def topic(self):
            for data in TEST_DATA:
                yield data

        class VerifyDefaultValueContext(Vows.Context):
            def topic(self, data):
                key, default_value = data
                cfg = Config()
                return (getattr(cfg, key), default_value)

            def should_have_default_value(self, topic):
                expect(topic).not_to_be_an_error()
                expect(topic).to_length(2)
                actual, expected = topic
                expect(actual).not_to_be_null()
                expect(actual).to_equal(expected)

    class WhenSettingAnAlias(Vows.Context):

        def topic(self):
            Config.alias('OTHER_ENGINE', 'ENGINE')
            return Config(OTHER_ENGINE='x')

        def should_set_engine_attribute(self, config):
            expect(config.ENGINE).to_equal('x')

        def should_set_other_engine_attribute(self, config):
            expect(config.OTHER_ENGINE).to_equal('x')

    class WhenSettingAnAliasedKey(Vows.Context):
        def topic(self):
            Config.alias('LOADER_ALIAS', 'LOADER')
            return Config(LOADER='y')

        def should_set_loader_attribute(self, config):
            expect(config.LOADER).to_equal('y')

        def should_set_loader_alias_attribute(self, config):
            expect(config.LOADER_ALIAS).to_equal('y')

    class WithAliasedAliases(Vows.Context):
        def topic(self):
            Config.alias('STORAGE_ALIAS', 'STORAGE')
            Config.alias('STORAGE_ALIAS_ALIAS', 'STORAGE_ALIAS')
            return Config(STORAGE_ALIAS_ALIAS='z')

        def should_set_storage_attribute(self, config):
            expect(config.STORAGE).to_equal('z')

        def should_set_storage_alias_attribute(self, config):
            expect(config.STORAGE_ALIAS).to_equal('z')

        def should_set_storage_alias_alias_attribute(self, config):
            expect(config.STORAGE_ALIAS_ALIAS).to_equal('z')

        class WithDefaultValues(Vows.Context):
            def topic(self):
                return Config()

            def should_set_storage_attribute(self, config):
                expect(config.STORAGE).to_equal(STORAGE_DEFAULT_VALUE)

            def should_set_storage_alias_attribute(self, config):
                expect(config.STORAGE_ALIAS).to_equal(STORAGE_DEFAULT_VALUE)

            def should_set_storage_alias_alias_attribute(self, config):
                expect(config.STORAGE_ALIAS_ALIAS).to_equal(STORAGE_DEFAULT_VALUE)

            def should_be_a_derpconf(self, config):
                expect(config.__class__.__module__).to_equal('derpconf.config')
