#!/usr/bin/env python
#-*- coding: utf8 -*-

import redis
from datetime import datetime, timedelta
from tornado.options import options, define

define('REDIS_SERVER', default={
    'port': 6379,
    'host': 'localhost',
    'db': 0
})

def put(path, bytes):
    storage = redis.Redis(**options.REDIS_SERVER)
    storage.set(path, bytes)
    storage.expireat(path, datetime.now() + timedelta(seconds=options.STORAGE_EXPIRATION_SECONDS))
    

def get(path):
    storage = redis.Redis(**options.REDIS_SERVER)
    return storage.get(path)

