#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os
from os.path import join, abspath, dirname, expanduser, exists

import tornado.web
import tornado.ioloop
from tornado.options import parse_config_file

from thumbor.config import conf
from thumbor.handlers.unsafe import MainHandler
from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.handlers.crypto import CryptoHandler
from thumbor.utils import real_import, logger
from thumbor.url import Url

class ThumborServiceApp(tornado.web.Application):

    def __init__(self, conf_file=None, custom_handlers=None):
        if conf_file is None:
            conf_file = ThumborServiceApp.get_conf_file(conf_file)

        logger.info('Config file: %s' % conf_file)
        parse_config_file(conf_file)

        self.loader = real_import(conf.LOADER)
        self.storage = real_import(conf.STORAGE)
        self.engine = real_import(conf.ENGINE)
        self.detectors = [real_import(detector_name).Detector for detector_name in conf.DETECTORS]
        #filters = [real_import(filter_name).Filter for filter_name in conf.FILTERS]
        filters = []

        # run again to overwrite the default settings on the
        # imported modules with the ones defined into the config file
        parse_config_file(conf_file)

        #storage = storage.Storage()
        #self.engine = self.engine.Engine()

        handler_context = {
            'loader': self.loader,
            'storage': self.storage,
            'engine': self.engine,
            'detectors': self.detectors,
            'filters': filters
        }

        handlers = [
            (r'/healthcheck', HealthcheckHandler)
        ]

        if conf.ALLOW_UNSAFE_URL:
            handlers.append(
                (Url.regex(), MainHandler, handler_context),
            )

        if custom_handlers:
            for handler in custom_handlers:
                handlers.append((handler[0], handler[1], handler_context))
        else:
            handlers.append(
                (r'/(?P<crypto>[^/]+)/(?P<image>(.+))', CryptoHandler, handler_context)
            )

        super(ThumborServiceApp, self).__init__(handlers)

    @classmethod
    def get_conf_file(cls, conf_file):
        lookup_conf_file_paths = [
            os.curdir,
            expanduser('~'),
            '/etc/',
            dirname(__file__)
        ]
        for conf_path in lookup_conf_file_paths:
            conf_path_file = abspath(join(conf_path, 'thumbor.conf'))
            if exists(conf_path_file):
                return conf_path_file

        raise ConfFileNotFoundError('thumbor.conf file not passed and not found on the lookup paths %s' % lookup_conf_file_paths)

class ConfFileNotFoundError(RuntimeError):
    pass
