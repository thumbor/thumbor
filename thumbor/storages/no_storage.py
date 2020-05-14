#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Optional

from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    async def put(self, path: str, file_bytes: bytes) -> Optional[str]:
        return path

    async def put_crypto(self, path: str) -> Optional[str]:
        return path

    async def put_detector_data(self, path: str, data: str) -> Optional[str]:
        return path

    async def get_crypto(self, path: str) -> Optional[str]:
        return None

    async def get_detector_data(self, path: str) -> Optional[str]:
        return None

    async def get(self, path: str) -> Optional[bytes]:
        return None

    async def exists(self, path: str) -> bool:
        return False

    async def remove(self, path):
        pass
