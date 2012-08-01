#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

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
    ('LOADER',  'thumbor.loaders.http_loader'),
    ('STORAGE', STORAGE_DEFAULT_VALUE),
    ('ENGINE', 'thumbor.engines.pil'),
    ('ALLOW_UNSAFE_URL', True),
    ('FILE_LOADER_ROOT_PATH', '/tmp'),
    ('MAX_SOURCE_SIZE', 0),
    ('REQUEST_TIMEOUT_SECONDS', 120),
    ('STORAGE_EXPIRATION_SECONDS', 60 * 60 * 24 * 30),
    ('STORES_CRYPTO_KEY_FOR_EACH_IMAGE', False),
    ('MONGO_STORAGE_SERVER_HOST', 'localhost'),
    ('MONGO_STORAGE_SERVER_PORT', 27017),
    ('MONGO_STORAGE_SERVER_DB', 'thumbor'),
    ('MONGO_STORAGE_SERVER_COLLECTION', 'images'),
    ('REDIS_STORAGE_SERVER_HOST', 'localhost'),
    ('REDIS_STORAGE_SERVER_PORT', 6379),
    ('REDIS_STORAGE_SERVER_DB', 0),
    ('MIXED_STORAGE_FILE_STORAGE', 'thumbor.storages.no_storage'),
    ('MIXED_STORAGE_CRYPTO_STORAGE', 'thumbor.storages.no_storage'),
    ('MIXED_STORAGE_DETECTOR_STORAGE', 'thumbor.storages.no_storage'),
    ('DETECTORS', []),
    ('FACE_DETECTOR_CASCADE_FILE', 'haarcascade_frontalface_alt.xml'),
    ('FILTERS', [])
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

#class ConfigContext(Vows.Context):
    #def _camel_split(self, string):
        #return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z])|(?=[0-9]\b))', ' ', string).strip()

    #def _config_name(self):
        #return '_'.join(self._camel_split(self.__class__.__name__).split(' ')).upper()

    #def topic(self):
        #config = self._config_name()
        #return getattr(conf, config)

    #def is_not_an_error(self, topic):
        #expect(topic).not_to_be_an_error()

#class NumericConfigContext(ConfigContext):

    #def is_numeric(self, topic):
        #expect(topic).to_be_numeric()

#@Vows.batch
#class Configuration(Vows.Context):

    #class Defaults(Vows.Context):

        ##class SecurityKey(ConfigContext):

            ##def defaults_to_null(self, topic):

                ##expect(topic).to_be_null()

        #class AllowUnsafeUrl(ConfigContext):

            #def defaults_to_true(self, topic):
                #expect(topic).to_be_true()

        #class MaxWidth(NumericConfigContext):

            #def defaults_to_0(self, topic):
                #expect(topic).to_equal(0)

        #class MaxHeight(NumericConfigContext):

            #def defaults_to_0(self, topic):
                #expect(topic).to_equal(0)

        ##class AllowedSources(ConfigContext):

            ##def defaults_to_empty(self, topic):
                ##expect(topic).to_be_empty()

        #class Quality(NumericConfigContext):

            #def defaults_to_85(self, topic):
                #expect(topic).to_equal(85)

        ##class Loader(ConfigContext):

            ##def defaults_to_http_loader(self, topic):
                ##expect(topic).to_equal('thumbor.loaders.http_loader')

        #class MaxSourceSize(NumericConfigContext):

            #def defaults_to_0(self, topic):
                #expect(topic).to_equal(0)

        #class RequestTimeoutSeconds(NumericConfigContext):

            #def defaults_to_120(self, topic):
                #expect(topic).to_equal(120)

        #class Engine(ConfigContext):

            #def defaults_to_pil(self, topic):
                #expect(topic).to_equal('thumbor.engines.pil')

        #class Storage(ConfigContext):

            #def defaults_to_file_storage(self, topic):
                #expect(topic).to_equal('thumbor.storages.file_storage')

            #class StorageExpirationSeconds(NumericConfigContext):

                #def defaults_to_one_month(self, topic):
                    #expect(topic).to_equal(60 * 60 * 24 * 30)

            #class MongoStorage(Vows.Context):

                #class MongoStorageServerHost(ConfigContext):

                    #def defaults_to_localhost(self, topic):
                        #expect(topic).to_equal('localhost')

                #class MongoStorageServerPort(NumericConfigContext):

                    #def defaults_to_27017(self, topic):
                        #expect(topic).to_equal(27017)

                #class MongoStorageServerDb(ConfigContext):

                    #def defaults_to_thumbor(self, topic):
                        #expect(topic).to_equal('thumbor')

                #class MongoStorageServerCollection(ConfigContext):

                    #def defaults_to_images(self, topic):
                        #expect(topic).to_equal('images')

            #class RedisStorage(Vows.Context):

                #class RedisStorageServerHost(ConfigContext):

                    #def defaults_to_localhost(self, topic):
                        #expect(topic).to_equal('localhost')

                #class RedisStorageServerPort(NumericConfigContext):

                    #def defaults_to_6379(self, topic):
                        #expect(topic).to_equal(6379)

                #class RedisStorageServerDb(NumericConfigContext):

                    #def defaults_to_0(self, topic):
                        #expect(topic).to_equal(0)

            #class MySqlStorage(Vows.Context):

                #class MysqlStorageServerHost(ConfigContext):

                    #def defaults_to_localhost(self, topic):
                        #expect(topic).to_equal('localhost')

                #class MysqlStorageServerPort(NumericConfigContext):

                    #def defaults_to_3306(self, topic):
                        #expect(topic).to_equal(3306)

                #class MysqlStorageServerUser(ConfigContext):

                    #def defaults_to_root(self, topic):
                        #expect(topic).to_equal('root')

                #class MysqlStorageServerPassword(ConfigContext):

                    #def defaults_to_empty(self, topic):
                        #expect(topic).to_be_empty()

                #class MysqlStorageServerDb(ConfigContext):

                    #def defaults_to_thumbor(self, topic):
                        #expect(topic).to_equal('thumbor')

                #class MysqlStorageServerTable(ConfigContext):

                    #def defaults_to_images(self, topic):
                        #expect(topic).to_equal('images')

        #class Engines(Vows.Context):

            #class ImageMagick(Vows.Context):

                #class MagickwandPath(ConfigContext):

                    #def defaults_to_empty(self, topic):
                        #expect(topic).to_be_empty()

            #class Json(Vows.Context):

                #class MetaCallbackName(ConfigContext):

                    #def defaults_to_null(self, topic):
                        #expect(topic).to_be_null()

        #class Detectors(ConfigContext):

            #def default_includes_face_detector(self, topic):
                #expect(topic).to_include('thumbor.detectors.face_detector')

            #def default_includes_feature_detector(self, topic):
                #expect(topic).to_include('thumbor.detectors.feature_detector')

            #class FaceDetector(Vows.Context):
                #class FaceDetectorCascadeFile(ConfigContext):

                    #def defaults_to_haarcascade_frontalface_alt(self, topic):
                        #expect(topic).to_equal('haarcascade_frontalface_alt.xml')

