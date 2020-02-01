#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import exists


class BaseStorage:
    def __init__(self, context):
        self.context = context

    async def put(self, path, file_bytes):
        """
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        """
        raise NotImplementedError()

    async def put_crypto(self, path):
        """
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        """
        raise NotImplementedError()

    async def put_detector_data(self, path, data):
        """
        :returns: Nothing. This method is expected to be asynchronous.
        :rtype: None
        """
        raise NotImplementedError()

    async def get_crypto(self, path):
        raise NotImplementedError()

    async def get_detector_data(self, path):
        raise NotImplementedError()

    async def get(self, path):
        raise NotImplementedError()

    async def exists(self, path):
        raise NotImplementedError()

    async def remove(self, path):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError as err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise
