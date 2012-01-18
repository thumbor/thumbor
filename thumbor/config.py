#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import join, exists, expanduser, dirname, abspath
import imp
import tempfile

class ConfigurationError(RuntimeError):
    pass

class Config(object):
    class_defaults = {}

    @classmethod
    def define(cls, key, value):
        cls.class_defaults[key] = value

    @classmethod
    def get_conf_file(cls):
        lookup_conf_file_paths = [
            os.curdir,
            expanduser('~'),
            '/etc/',
            dirname(__file__)
        ]
        for conf_path in lookup_conf_file_paths:
            conf_path_file = abspath(join(conf_path, 'thumbor.conf'))
            if exists(conf_path_file):
                return conf_path_file

        raise ConfigurationError('thumbor.conf file not passed and not found on the lookup paths %s' % lookup_conf_file_paths)

    @classmethod
    def load(cls, path):
        if path is None:
            path = cls.get_conf_file()

        with open(path) as config_file:
            name='configuration'
            code = config_file.read()
            module = imp.new_module(name)
            exec code in module.__dict__

            conf = cls()
            conf.config_file = config_file
            for name, value in module.__dict__.iteritems():
                setattr(conf, name, value)

            return conf

    def __init__(self, **kw):
        if 'defaults' in kw:
            self.defaults = kw['defaults']

        for key, value in kw.iteritems():
            setattr(self, key, value)

    def validates_presence_of(self, *args):
        for arg in args:
            if not hasattr(self, arg):
                raise ConfigurationError('Configuration %s was not found and does not have a default value. Please verify your thumbor.conf file' % arg)

    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)
        return default

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
Config.define('MAX_AGE', 0)

Config.define('LOADER',  'thumbor.loaders.http_loader')
Config.define('STORAGE', 'thumbor.storages.file_storage')
Config.define('RESULT_STORAGE', None)
Config.define('ENGINE', 'thumbor.engines.pil')

Config.define('SECURITY_KEY', 'MY_SECURE_KEY')

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

# RESULT STORAGE
Config.define('RESULT_STORAGE_EXPIRATION_SECONDS', 0) # Never expires
Config.define('RESULT_STORAGE_FILE_STORAGE_ROOT_PATH', join(tempfile.gettempdir(), 'thumbor', 'result_storage'))
Config.define('RESULT_STORAGE_STORES_UNSAFE', False)
