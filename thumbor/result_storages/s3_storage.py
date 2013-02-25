#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from thumbor.result_storages import BaseStorage
from thumbor.utils import logger


class Storage(BaseStorage):

    re_remove_yipitcdn_domain = re.compile(r'(?:http:\/\/)?[a-z]\.yipitcdn\.com\/')

    def __init__(self, context):
        super(self.__class__, self).__init__(context)
        config = self.context.config
        self.conn = S3Connection(
            config.RESULT_STORAGE_S3_ACCESS_KEY_ID,
            config.RESULT_STORAGE_S3_SECRET_ACCESS_KEY,
        )
        self.bucket = self.conn.get_bucket(config.RESULT_STORAGE_S3_BUCKET_NAME)

    def put(self, bytes):
        file_abspath = self.__normalize_path(self.context.request.url)
        logger.debug("[RESULT_STORAGE] putting at %s" % file_abspath)
        self.__write(file_abspath, bytes)

    def get(self):
        file_abspath = self.__normalize_path(self.context.request.url)
        logger.debug("[RESULT_STORAGE] getting from %s" % file_abspath)
        return self.__read(file_abspath)

    def __normalize_path(self, path):
        #return path
        return self.re_remove_yipitcdn_domain.sub('', path, count=1)

    def __write(self, key_name, bytes):
        key = Key(self.bucket)
        key.key = key_name
        key.set_contents_from_string(bytes)

    def __read(self, key_name):
        key = self.bucket.get_key(key_name)
        if key is None:
            logger.debug("[RESULT_STORAGE] image not found at %s" % key_name)
            return None
        return key.get_contents_as_string()
