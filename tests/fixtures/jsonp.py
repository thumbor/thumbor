#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

META_CALLBACK_NAME = 'callback'

LOADER = 'thumbor.loaders.http_loader'

STORAGE = 'thumbor.storages.file_storage'

FILE_STORAGE_ROOT_PATH = "/tmp/thumbor/storage"

# this is the security key used to encrypt/decrypt urls.
# make sure this is unique and not well-known
# This can be any string of up to 24 characters
SECURITY_KEY = "MY_SECURE_KEY"

# if you enable this, the unencryted URL will be available
# to users.
# IT IS VERY ADVISED TO SET THIS TO False TO STOP OVERLOADING
# OF THE SERVER FROM MALICIOUS USERS
ALLOW_UNSAFE_URL = True
