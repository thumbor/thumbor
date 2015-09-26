#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

ALLOWED_SOURCES = ['s.glbimg.com']

SECURITY_KEY = 'HandlerVows'

LOADER = 'thumbor.loaders.file_loader'
FILE_LOADER_ROOT_PATH = './vows/fixtures'
