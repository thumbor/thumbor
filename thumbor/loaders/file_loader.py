#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join

from thumbor.config import conf

def load(path,callback):
    callback(open(join(conf.FILE_LOADER_ROOT_PATH.rstrip('/'), path.lstrip('/'))).read())