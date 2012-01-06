#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join
import tempfile

from tornado.options import options, define

define('MAX_WIDTH', type=int, default=0)
define('MAX_HEIGHT', type=int, default=0)
define('MAX_AGE',type=int, default=0)
define('ALLOWED_SOURCES', default=[], multiple=True)
define('QUALITY', type=int, default=80)

define('LOADER',  default='thumbor.loaders.http_loader')
define('STORAGE', default='thumbor.storages.file_storage')
define('ENGINE', default='thumbor.engines.pil')

define('SECURITY_KEY', type=str)
define('ALLOW_UNSAFE_URL', type=bool, default=True)

# FILE LOADER OPTIONS
define('FILE_LOADER_ROOT_PATH')

# HTTP LOADER OPTIONS
define('MAX_SOURCE_SIZE', type=int, default=0)
define('REQUEST_TIMEOUT_SECONDS', type=int, default=120)

# FILE STORAGE GENERIC OPTIONS
define('STORAGE_EXPIRATION_SECONDS', type=int, default=60 * 60 * 24 * 30) # default one month
define('STORES_CRYPTO_KEY_FOR_EACH_IMAGE', type=bool, default=False)

# FILE STORAGE OPTIONS
define('FILE_STORAGE_ROOT_PATH', default=join(tempfile.gettempdir(), 'thumbor', 'storage'))

# MONGO STORAGE OPTIONS
define('MONGO_STORAGE_SERVER_HOST', type=str, default='localhost')
define('MONGO_STORAGE_SERVER_PORT', type=int, default=27017)
define('MONGO_STORAGE_SERVER_DB', type=str, default='thumbor')
define('MONGO_STORAGE_SERVER_COLLECTION', type=str, default='images')

# REDIS STORAGE OPTIONS
define('REDIS_STORAGE_SERVER_HOST', type=str, default='localhost')
define('REDIS_STORAGE_SERVER_PORT', type=int, default=6379)
define('REDIS_STORAGE_SERVER_DB', type=int, default=0)

# MYSQL STORAGE OPTIONS
define('MYSQL_STORAGE_SERVER_HOST', type=str, default='localhost')
define('MYSQL_STORAGE_SERVER_PORT', type=int, default=3306)
define('MYSQL_STORAGE_SERVER_USER', type=str, default='root')
define('MYSQL_STORAGE_SERVER_PASSWORD', type=str, default='')
define('MYSQL_STORAGE_SERVER_DB', type=str, default='thumbor')
define('MYSQL_STORAGE_SERVER_TABLE', type=str, default='images')

# MIXED STORAGE OPTIONS
define('MIXED_STORAGE_FILE_STORAGE', type=str, default='thumbor.storages.no_storage')
define('MIXED_STORAGE_CRYPTO_STORAGE', type=str, default='thumbor.storages.no_storage')
define('MIXED_STORAGE_DETECTOR_STORAGE', type=str, default='thumbor.storages.no_storage')

# ImageMagick ENGINE OPTIONS
define('MAGICKWAND_PATH', default=[], multiple=True)

# JSON META ENGINE OPTIONS
define('META_CALLBACK_NAME', type=str, default=None)

# DETECTORS OPTIONS
define('DETECTORS', default=['thumbor.detectors.face_detector', 'thumbor.detectors.feature_detector'], multiple=True)

# FACE DETECTOR CASCADE FILE
define('FACE_DETECTOR_CASCADE_FILE', default='haarcascade_frontalface_alt.xml')

# REMOTE FACE DETECTION
define('REMOTECV_HOST', type=str, default="localhost")
define('REMOTECV_PORT', type=int, default=13337)
define('REMOTECV_TIMEOUT', type=int, default=20)
define('REMOTECV_SEND_IMAGE', type=bool, default=True)

# AVAILABLE FILTERS
define('FILTERS', default=[], multiple=True)

class ConfigWrapper(object):

    def __getattr__(self, name):
        return getattr(options, name)

conf = ConfigWrapper()
