#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.storages import BaseStorage
from tornado import gen


class Storage(BaseStorage):

    def put(self, path, bytes):
        return path

    def put_crypto(self, path):
        return path

    def put_detector_data(self, path, data):
        return path

    @gen.coroutine
    def get_crypto(self, path):
        raise gen.Return(None)

    @gen.coroutine
    def get_detector_data(self, path):
        raise gen.Return(None)

    @gen.coroutine
    def get(self, path):
        raise gen.Return(None)

    @gen.coroutine
    def exists(self, path):
        raise gen.Return(None)

    def remove(self, path):
        pass
