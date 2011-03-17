#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join
import urllib2

def load(path):
    if not path.startswith('http'):
        path = join('http://', path)

    response = urllib2.urlopen(path)
    return response.read()
    