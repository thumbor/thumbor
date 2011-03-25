#!/usr/bin/env python
#-*- coding: utf8 -*-


from datetime import datetime, timedelta

import redis
from tornado.options import options, define

from thumbor.storages import BaseStorage


define('REDIS_SERVER', default={
    'port': 6379,
    'host': 'localhost',
    'db': 0
})


class Storage(BaseStorage):

    def __init__(self):
        self.storage = redis.Redis(**options.REDIS_SERVER)

    def put(self, path, bytes):
        self.storage.set(path, bytes)
        self.storage.expireat(path, datetime.now() + timedelta(seconds=options.STORAGE_EXPIRATION_SECONDS))

    def get(self, path):
        return self.storage.get(path)

