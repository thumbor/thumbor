#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2015 popsugar.com vtodorov@popsugar.com
from thumbor.result_storages import BaseStorage
from tornado.concurrent import return_future


class Storage(BaseStorage):
    def put(self, bytes):
        return ''

    @return_future
    def get(self, callback):
        callback(None)
