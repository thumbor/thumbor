#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse

import tornado.httpclient

from thumbor.config import conf
http_client = None

def _normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(url):
    if not conf.ALLOWED_SOURCES:
        return True

    url = _normalize_url(url)
    res = urlparse(url)
    for pattern in conf.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

#def verify_size(url, max_size):
    #usock = urllib2.urlopen(url)
    #actual = usock.info().get('Content-Length')
    #if actual is None:
        #actual = 0
    #return (float(actual) / 1024) <= max_size

def load(url, callback):
    client = http_client
    if client is None:
        client = tornado.httpclient.AsyncHTTPClient()
    #if conf.MAX_SOURCE_SIZE and not verify_size(url, conf.MAX_SOURCE_SIZE):
        #return None

    def return_contents(response):
        if response.error:
            callback(None, None)
        else:
            callback(response.body, response.headers.get_list('Content-type')[0])

    url = _normalize_url(url)
    client.fetch(url, callback=return_contents)

