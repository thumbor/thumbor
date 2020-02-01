#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
from os.path import abspath

LOADER = "thumbor.loaders.file_loader"
FILE_LOADER_ROOT_PATH = abspath("./tests/fixtures/images/")
STORAGE = "thumbor.storages.no_storage"

MAX_AGE = 2
MAX_AGE_TEMP_IMAGE = 1
