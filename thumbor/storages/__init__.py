#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import exists
from typing import Any, Optional


class BaseStorage:
    def __init__(self, context):
        self.context = context

    async def initialize(self, context: Any) -> None:
        """
        Initializes the storage. This method is called when thumbor starts up.
        It is useful for allocating expensive resources like pools.
        """
        pass

    async def shutdown(self, context: Any) -> None:
        """
        Shuts the storage down. This method is called when thumbor stops.
        It is useful for deallocating expensive resources like pools.
        """
        pass

    async def put(self, path: str, file_bytes: bytes) -> Optional[str]:
        """
        Puts an image in storage.
        Optionally returns path information for the file placed in storage.
        """
        raise NotImplementedError()

    async def put_crypto(self, path: str) -> Optional[str]:
        """
        Puts cryptographic information about the image in the storage.
        This is useful for generating the same image again if thumbor's key changes.
        Optionally returns path information for the data placed in storage.
        """
        raise NotImplementedError()

    async def put_detector_data(self, path: str, data: str) -> Optional[str]:
        """
        Puts smart detection data in the storage. This is useful for not querying
        detection again in the next image crop.
        Optionally returns path information for the data placed in storage.
        """
        raise NotImplementedError()

    async def get_crypto(self, path: str) -> Optional[str]:
        raise NotImplementedError()

    async def get_detector_data(self, path: str) -> Optional[str]:
        raise NotImplementedError()

    async def get(self, path: str) -> Optional[bytes]:
        raise NotImplementedError()

    async def exists(self, path: str) -> bool:
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
