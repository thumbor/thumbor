#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import exists
from tornado.concurrent import return_future

from thumbor.loaders import LoaderResult
from thumbor.engines import BaseEngine


class ResultStorageResult(LoaderResult):
    @property
    def last_modified(self):
        '''
        Retrieves last_updated metadata if available
        :return:
        '''
        return self.metadata.get('LastModified', None)

    @property
    def mime(self):
        '''
        Retrieves mime metadata if available
        :return:
        '''
        return self.metadata['ContentType'] if 'ContentType' in self.metadata else BaseEngine.get_mimetype(self.buffer)

    def __len__(self):
        return self.metadata['ContentLength'] if 'ContentLength' in self.metadata else len(self.buffer)


class BaseStorage(object):

    is_media_aware = False

    def __init__(self, context):
        self.context = context

    def put(self, bytes):
        raise NotImplementedError()

    @return_future
    def get(self, callback):
        raise NotImplementedError()

    def last_updated(self):
        raise NotImplementedError()

    def ensure_dir(self, path):
        if not exists(path):
            try:
                os.makedirs(path)
            except OSError, err:
                # FILE ALREADY EXISTS = 17
                if err.errno != 17:
                    raise
