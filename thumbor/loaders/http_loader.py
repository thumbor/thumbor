#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from urlparse import urlparse

import eventlet
from eventlet.green import urllib2
from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.options import define, options

define('ALLOWED_SOURCES', default=[], multiple=True)
define('MAX_SOURCE_SIZE', type=int, default=0)
define('REQUEST_TIMEOUT_SECONDS', type=int, default=120)

pool = eventlet.GreenPool()

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
    def verify(options):
        source, size = options

        usock = urllib2.urlopen(source)
        actual = usock.info().get('Content-Length')
        if actual is None:
            actual = 0
        return (float(actual) / 1024) <= size

    for verified in pool.imap(verify, [(__normalize_url(url), max_size)]):
        return verified

def load(url, callback):
    if options.MAX_SOURCE_SIZE and not verify_size(url, options.MAX_SOURCE_SIZE):
        return None

    def actual_load(actual_url):
        usock = urllib2.urlopen(actual_url, timeout=options.REQUEST_TIMEOUT_SECONDS)

        try:
            return usock.read()
        except urllib2.HTTPError:
            return None

    func = pool.spawn(actual_load, url)

    def return_contents(gt, url, callback):
        contents = gt.wait()

        callback(contents)

    func.link(return_contents, url, callback)

