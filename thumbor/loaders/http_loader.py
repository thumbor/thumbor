#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
from urlparse import urlparse

import tornado.httpclient
from tornado.options import options

def __normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(url):
    url = __normalize_url(url)
    res = urlparse(url)
    for pattern in options.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def load(url, callback):
    url = __normalize_url(url)
    http = tornado.httpclient.AsyncHTTPClient()
    def load_callback(response):
        if response.code == 200:
            callback(response.body)
        else:
            callback(None)
    http.fetch(url, callback=load_callback)