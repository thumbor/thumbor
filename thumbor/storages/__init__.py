#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import exists
from tornado import gen


class BaseStorage(object):
    def __init__(self, context):
        self.context = context

    def put(self, path, bytes):
        '''
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        '''
        raise NotImplementedError()

    def put_crypto(self, path):
        '''
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        '''
        raise NotImplementedError()

    def put_detector_data(self, path, data):
        '''
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        '''
        raise NotImplementedError()

    @gen.coroutine
    def get_crypto(self, path):
        raise NotImplementedError()

    @gen.coroutine
    def get_detector_data(self, path):
        raise NotImplementedError()

    @gen.coroutine
    def get(self, path):
        raise NotImplementedError()

    @gen.coroutine
    def exists(self, path):
        raise NotImplementedError()

    def remove(self, path):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError, err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise
