#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.storages import BaseStorage

class Storage(BaseStorage):

    def put(self, path, bytes):
        pass

    def put_crypto(self, path):
        pass

    def get_crypto(self, path):
        return None

    def get(self, path):
        return None
