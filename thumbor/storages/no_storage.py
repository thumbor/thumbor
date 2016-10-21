#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.storages import BaseStorage
from tornado.concurrent import return_future


class Storage(BaseStorage):

    def put(self, path, bytes):
        return path

    def put_crypto(self, path):
        return path

    def put_detector_data(self, path, data):
        return path

    @return_future
    def get_crypto(self, path, callback):
        callback(None)

    @return_future
    def get_detector_data(self, path, callback):
        callback(None)

    @return_future
    def get(self, path, callback):
        callback(None)

    @return_future
    def exists(self, path, callback):
        callback(False)

    def remove(self, path):
        pass
