#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''
RequestDetails is a data container for request data.
'''

from tornado import gen
from thumbor.config_wrapper import ConfigWrapper


class RequestDetails(object):  # pylint: disable=too-many-instance-attributes
    'Details for a given image request'

    def __init__(self, config, filters_map, request_parameters=None):
        self.mimetype = None
        self.finish_early = False
        self.status_code = 200
        self.body = None
        self.headers = {}
        self.source_image = None
        self.transformed_image = None
        self.request_parameters = request_parameters
        self._config = config
        self.config = ConfigWrapper(config)
        self.metadata = {}
        self.filters = filters_map
        self.target_width = 0
        self.target_height = 0
        self.focal_points = []

    @gen.coroutine
    def run_filters(self):
        '''
        Determine which filters should be executed for the current request.
        '''
        if self.request_parameters.filters:
            for values in self.filters:
                regex = values['regex']
                parsers = values['parsers']
                method = values['method']
                params = regex.match(
                    self.request_parameters.filters) if regex else None
                if params:
                    params = [
                        parser(param) if parser else param
                        for parser, param in zip(parsers, params.groups())
                        if param
                    ]
                    yield method(self, self, *params)

    def has_filter(self, name):
        'Determine if the current request has the specified filter'
        return name in self.filters

    def get_filter_arguments(self, name):
        'Get filter arguments by name'
        return self.filters.get(name, [])
