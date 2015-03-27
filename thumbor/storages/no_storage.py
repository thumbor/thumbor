#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.storages import BaseStorage


class Storage(BaseStorage):

    def put(self, path, bytes, callback):
        return path

    def put_crypto(self, path, callback):
        return path

    def put_detector_data(self, path, data, callback):
        return path

    def get_crypto(self, path, callback):
        return None

    def get_detector_data(self, path, callback):
        return None

    def get(self, path, callback):
        return None

    def exists(self, path, callback):
        return False

    def remove(self, path, callback):
        pass
