#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


class LoaderResult(object):

    ERROR_NOT_FOUND = 'not_found'
    ERROR_UPSTREAM = 'upstream'
    ERROR_TIMEOUT = 'timeout'

    def __init__(self, buffer=None, successful=True, error=None, metadata=dict()):
        '''
        :param buffer: The media buffer

        :param successful: True when the media has been loaded.
        :type successful: bool

        :param error: Error code
        :type error: str

        :param metadata: Dictionary of metadata about the buffer
        :type metadata: dict
        '''

        self.buffer = buffer
        self.successful = successful
        self.error = error
        self.metadata = metadata
