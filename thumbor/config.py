#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join
import tempfile

#from tornado.options import options, define

#class ConfigWrapper(object):

    #def __getattr__(self, name):
        #return getattr(options, name)

#conf = ConfigWrapper()

class ConfigurationError(RuntimeError):
    pass

class Config(object):
    class_defaults = {}

    @classmethod
    def define(cls, key, value):
        cls.class_defaults[key] = value

    @classmethod
    def load(cls, path):
        pass

    def __init__(self, **kw):
        if 'defaults' in kw:
            self.defaults = kw['defaults']

        for key, value in kw.iteritems():
            setattr(self, key, value)

    def validates_presence_of(self, *args):
        for arg in args:
            if not hasattr(self, arg):
                raise ConfigurationError('Configuration %s was not found and does not have a default value. Please verify your thumbor.conf file' % arg)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        if 'defaults' in self.__dict__ and name in self.__dict__['defaults']:
            return self.__dict__['defaults'][name]

        if name in Config.class_defaults:
            return Config.class_defaults[name]

        raise AttributeError(name)

Config.define('MAX_WIDTH', 0)
Config.define('MAX_HEIGHT', 0)
Config.define('ALLOWED_SOURCES', [])
Config.define('QUALITY', 80)

Config.define('LOADER',  'thumbor.loaders.http_loader')
Config.define('STORAGE', 'thumbor.storages.file_storage')
Config.define('ENGINE', 'thumbor.engines.pil')

Config.define('ALLOW_UNSAFE_URL', True)

# FILE LOADER OPTIONS
Config.define('FILE_LOADER_ROOT_PATH', '/tmp')

# HTTP LOADER OPTIONS
Config.define('MAX_SOURCE_SIZE', 0)
Config.define('REQUEST_TIMEOUT_SECONDS', 120)

# FILE STORAGE GENERIC OPTIONS
Config.define('STORAGE_EXPIRATION_SECONDS', 60 * 60 * 24 * 30) # default one month
Config.define('STORES_CRYPTO_KEY_FOR_EACH_IMAGE', False)

# FILE STORAGE OPTIONS
Config.define('FILE_STORAGE_ROOT_PATH', join(tempfile.gettempdir(), 'thumbor', 'storage'))

# MONGO STORAGE OPTIONS
Config.define('MONGO_STORAGE_SERVER_HOST', 'localhost')
Config.define('MONGO_STORAGE_SERVER_PORT', 27017)
Config.define('MONGO_STORAGE_SERVER_DB', 'thumbor')
Config.define('MONGO_STORAGE_SERVER_COLLECTION', 'images')

# REDIS STORAGE OPTIONS
Config.define('REDIS_STORAGE_SERVER_HOST', 'localhost')
Config.define('REDIS_STORAGE_SERVER_PORT', 6379)
Config.define('REDIS_STORAGE_SERVER_DB', 0)

# MYSQL STORAGE OPTIONS
Config.define('MYSQL_STORAGE_SERVER_HOST', 'localhost')
Config.define('MYSQL_STORAGE_SERVER_PORT', 3306)
Config.define('MYSQL_STORAGE_SERVER_USER', 'root')
Config.define('MYSQL_STORAGE_SERVER_PASSWORD', '')
Config.define('MYSQL_STORAGE_SERVER_DB', 'thumbor')
Config.define('MYSQL_STORAGE_SERVER_TABLE', 'images')

# MIXED STORAGE OPTIONS
Config.define('MIXED_STORAGE_FILE_STORAGE', 'thumbor.storages.no_storage')
Config.define('MIXED_STORAGE_CRYPTO_STORAGE', 'thumbor.storages.no_storage')
Config.define('MIXED_STORAGE_DETECTOR_STORAGE', 'thumbor.storages.no_storage')

# JSON META ENGINE OPTIONS
Config.define('META_CALLBACK_NAME', None)

# DETECTORS OPTIONS
Config.define('DETECTORS', ['thumbor.detectors.face_detector', 'thumbor.detectors.feature_detector'])

# FACE DETECTOR CASCADE FILE
Config.define('FACE_DETECTOR_CASCADE_FILE', 'haarcascade_frontalface_alt.xml')

# REMOTE FACE DETECTION
Config.define('REMOTECV_HOST', "localhost")
Config.define('REMOTECV_PORT', 13337)
Config.define('REMOTECV_TIMEOUT', 20)
Config.define('REMOTECV_SEND_IMAGE', True)

# AVAILABLE FILTERS
Config.define('FILTERS', [])

