#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime, timedelta

import redis
from tornado.options import options, define

from thumbor.storages import BaseStorage

define('REDIS_STORAGE_SERVER', default={
    'port': 6379,
    'host': 'localhost',
    'db': 0
})

class Storage(BaseStorage):

    def __init__(self):
        self.storage = redis.Redis(**options.REDIS_STORAGE_SERVER)

    def put(self, path, bytes):
        self.storage.set(path, bytes)
        self.storage.expireat(path, datetime.now() + timedelta(seconds=options.STORAGE_EXPIRATION_SECONDS))

    def get(self, path):
        return self.storage.get(path)

