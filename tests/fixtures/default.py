#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

# the domains that can have theyre images resized
ALLOWED_SOURCES = ['s.glbimg.com', 'www.globo.com']

# the max width of the resized image
MAX_WIDTH = 1280

# the max height of the resized image
MAX_HEIGHT = 800

LOADER = 'thumbor.loaders.http_loader'

STORAGE = 'thumbor.storages.file_storage'

FILE_STORAGE_ROOT_PATH = "/tmp/thumbor/storage"
