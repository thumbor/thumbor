#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Dict


class LoaderResult:
    ERROR_NOT_FOUND = "not_found"
    ERROR_UPSTREAM = "upstream"
    ERROR_TIMEOUT = "timeout"
    ERROR_BAD_REQUEST = "bad_request"

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        buffer: bytes = None,
        successful: bool = True,
        error: str = None,
        metadata: Dict[str, any] = None,
        extras: Dict[str, any] = None,
    ):
        """
        :param buffer: The media buffer

        :param successful: True when the media has been loaded.
        :type successful: bool

        :param error: Error code
        :type error: str

        :param metadata: Dictionary of metadata about the buffer
        :type metadata: dict

        :param extras: Dictionary of extra information about the error
        :type metadata: dict
        """

        if metadata is None:
            metadata = {}

        if extras is None:
            extras = {}

        self.buffer = buffer
        self.successful = successful
        self.error = error
        self.metadata = metadata
        self.extras = extras
