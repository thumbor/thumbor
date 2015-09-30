#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

STORAGE = 'thumbor.storages.file_storage'

# STORAGE SPECIFIC CONFIGURATIONS
FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/storage'

STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True

SECURITY_KEY = 'MY-SECURITY-KEY'
