#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse

from tornado.options import define, options
import tornado.httpclient

define('ALLOWED_SOURCES', default=[], multiple=True)
define('MAX_SOURCE_SIZE', type=int, default=0)
define('REQUEST_TIMEOUT_SECONDS', type=int, default=120)

#pool = eventlet.GreenPool()

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

#def verify_size(url, max_size, callback):
    #def verify(source, size):
        #usock = urllib2.urlopen(source)
        #actual = usock.info().get('Content-Length')
        #if actual is None:
            #actual = 0
        #return (float(actual) / 1024) <= size

    #func = pool.spawn(verify, url, max_size)

    #def return_verified(gt, url, callback):
        #is_valid = gt.wait()

        #callback(is_valid)

    #func.link(return_verified, url, callback)

def load(url, callback):
    #if options.MAX_SOURCE_SIZE and not verify_size(url, options.MAX_SOURCE_SIZE):
        #return None

    def return_contents(response):
        if response.error: callback(None)
        callback(response.body)

    http = tornado.httpclient.AsyncHTTPClient()
    url = __normalize_url(url)
    http.fetch(url, callback=return_contents)

