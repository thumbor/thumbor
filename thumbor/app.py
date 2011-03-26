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
from tornado.options import define, options, parse_config_file

from thumbor.handlers import MainHandler, HealthcheckHandler
from thumbor.utils import real_import, logger

define('ENGINE',  default='thumbor.engines.pil')
define('LOADER',  default='thumbor.loaders.http_loader')
define('STORAGE', default='thumbor.storages.file_storage')
define('STORAGE_EXPIRATION_SECONDS', type=int, default=60 * 60 * 24 * 30) # default one month
define('DETECTORS', default=['thumbor.detectors.face_detector', 'thumbor.detectors.feature_detector'], multiple=True)

class ThumborServiceApp(tornado.web.Application):

    def __init__(self, conf_file=None):

        if conf_file is None:
            conf_file = self.__get_conf_file(conf_file)

        logger.info('Config file: %s' % conf_file)
        parse_config_file(conf_file)

        loader = real_import(options.LOADER)
        storage = real_import(options.STORAGE)
        engine = real_import(options.ENGINE)

        detectors = []
        for detector_name in options.DETECTORS:
            detectors.append(real_import(detector_name).Detector)

        # run again to overwrite the default settings on the
        # imported modules with the ones defined into the config file
        parse_config_file(conf_file)

        storage = storage.Storage()
        engine = engine.Engine()

        handlers = [
            (r'/healthcheck', HealthcheckHandler),
            (r'/(?:(meta)/)?(?:(\d+)x(\d+):(\d+)x(\d+)/)?(?:(-)?(\d+)?x(-)?(\d+)?/)?(?:(left|right|center)/)?(?:(top|bottom|middle)/)?(?:(smart)/)?(.+)', MainHandler, {
                'loader': loader,
                'storage': storage,
                'engine': engine,
                'detectors': detectors
            }),
        ]

        super(ThumborServiceApp, self).__init__(handlers)

    def __get_conf_file(self, conf_file):
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
