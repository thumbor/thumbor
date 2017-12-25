#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''
Wrapper responsible for handling request configuration.
'''


class ConfigWrapper(object):  # pylint: disable=too-few-public-methods
    'Configuration wrapper to ensure no leaking'

    def __init__(self, config):
        self._config = config

    def __getattr__(self, name):
        if name != '_config' and name not in self.__dict__:
            return getattr(self._config, name)
        return super(ConfigWrapper, self).__getattr__(name)  # pylint: disable=no-member
