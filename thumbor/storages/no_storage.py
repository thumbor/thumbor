#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    async def put(self, path, file_bytes):
        return path

    async def put_crypto(self, path):
        return path

    async def put_detector_data(self, path, data):
        return path

    async def get_crypto(self, path):
        return None

    async def get_detector_data(self, path):
        return None

    async def get(self, path):
        return None

    async def exists(self, path):
        return False

    async def remove(self, path):
        pass
