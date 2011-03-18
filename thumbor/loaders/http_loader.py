#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
import urllib2
from urlparse import urlparse
from os.path import join

import tornado.httpclient
from tornado.options import options, define


define('ALLOWED_SOURCES', type=str, default=['www.globo.com', 's.glbimg.com'], multiple=True)


def _normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def validate(url):
    url = _normalize_url(url)
    res = urlparse(url)
    for pattern in options.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def load(url, callback):
    url = _normalize_url(url)
    http = tornado.httpclient.AsyncHTTPClient()
    http.fetch(url, callback=callback)    