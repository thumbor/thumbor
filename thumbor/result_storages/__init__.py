#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import exists

from thumbor.engines import BaseEngine
from thumbor.loaders import LoaderResult


class ResultStorageResult(LoaderResult):
    @property
    def last_modified(self):
        """
        Retrieves last_updated metadata if available
        :return:
        """
        return self.metadata.get("LastModified", None)

    @property
    def mime(self):
        """
        Retrieves mime metadata if available
        :return:
        """
        return (
            self.metadata["ContentType"]
            if "ContentType" in self.metadata
            else BaseEngine.get_mimetype(self.buffer)
        )

    def __len__(self):
        return (
            self.metadata["ContentLength"]
            if "ContentLength" in self.metadata
            else len(self.buffer)
        )


class BaseStorage:
    def __init__(self, context):
        self.context = context

    async def put(self, image_bytes):
        raise NotImplementedError()

    async def get(self):
        raise NotImplementedError()

    def last_updated(self):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError as err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise
