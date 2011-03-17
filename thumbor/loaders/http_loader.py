#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
import urllib2
from urlparse import urlparse
from os.path import join


from tornado.options import options, define


define('ALLOWED_SOURCES', type=str, default=['www.globo.com', 's.glbimg.com'], multiple=True)


def _normalize_url(url):
    return url if url.startswith('http') else 'http://%s' % url

def resolve(url):
    return urlparse(_normalize_url(url)).path

def validate(url):
    url = _normalize_url(url)
    res = urlparse(url)
    for pattern in options.ALLOWED_SOURCES:
        if re.match('^%s$' % pattern, res.hostname):
            return True
    return False

def load(url):
    url = _normalize_url(url)
    response = urllib2.urlopen(url)
    return response.read()
    