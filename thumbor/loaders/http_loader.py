#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse
import urllib2

from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.options import define, options

define('ALLOWED_SOURCES', default=[], multiple=True)
define('MAX_SOURCE_SIZE', type=int, default=0)
define('REQUEST_TIMEOUT_SECONDS', type=int, default=120)

def __normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(url):
    if not options.ALLOWED_SOURCES:
        return True

    url = __normalize_url(url)
    res = urlparse(url)
    for pattern in options.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def verify_size(url, max_size):
    usock = urllib2.urlopen(__normalize_url(url))
    size =  usock.info().get('Content-Length')
    if size is None:
        size = 0
    return (float(size) / 1024) <= max_size

def load(url):
    if options.MAX_SOURCE_SIZE and not verify_size(url, options.MAX_SOURCE_SIZE):
        return None

    url = __normalize_url(url)
    http = HTTPClient()
    request = HTTPRequest(url=url, request_timeout=options.REQUEST_TIMEOUT_SECONDS)
    response = http.fetch(request)
    if response.code == 200:
        return response.body
    else:
        return None
