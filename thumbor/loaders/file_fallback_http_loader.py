#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.httpclient
from tornado.concurrent import return_future
import http_loader
import file_loader

@return_future
def load(context, path, callback, normalize_url_func=http_loader._normalize_url):
    if path.startswith('http'):
        http_loader.load_sync(context, path, callback, normalize_url_func)
    else:
        file_loader.load(context, path, callback)
