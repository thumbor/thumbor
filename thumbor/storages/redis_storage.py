#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import redis
from datetime import datetime, timedelta
from tornado.options import options, define


define('REDIS_SERVER', default={
    'port': 6379,
    'host': 'localhost',
    'db': 0
})

storage = None

def init():
    global storage
    storage = redis.Redis(**options.REDIS_SERVER)

def put(path, bytes):
    global storage
    storage.set(path, bytes)
    storage.expireat(path, datetime.now() + timedelta(seconds=options.STORAGE_EXPIRATION_SECONDS))

def get(path):
    global storage
    return storage.get(path)

