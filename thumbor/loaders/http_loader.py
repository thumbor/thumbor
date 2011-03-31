#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse

from tornado.httpclient import HTTPClient
from tornado.options import define, options


define('ALLOWED_SOURCES', default=['www.globo.com', 's.glbimg.com'], multiple=True)


def __normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(url):
    url = __normalize_url(url)
    res = urlparse(url)
    for pattern in options.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def load(url):
    url = __normalize_url(url)
    http = HTTPClient()
    response = http.fetch(url)
    if response.code == 200:
        return response.body
    else:
        return None
