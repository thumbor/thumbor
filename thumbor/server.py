#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import logging
import logging.config

import os
import socket
from os.path import expanduser, dirname

import tornado.ioloop
from tornado.httpserver import HTTPServer

from thumbor.console import get_server_parameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context
from thumbor.utils import which


def get_as_integer(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def get_config(config_path):
    lookup_paths = [os.curdir,
                    expanduser('~'),
                    '/etc/',
                    dirname(__file__)]

    return Config.load(config_path, conf_name='thumbor.conf', lookup_paths=lookup_paths)


def configure_log(config, log_level):
    if (config.THUMBOR_LOG_CONFIG and config.THUMBOR_LOG_CONFIG != ''):
        logging.config.dictConfig(config.THUMBOR_LOG_CONFIG)
    else:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=config.THUMBOR_LOG_FORMAT,
            datefmt=config.THUMBOR_LOG_DATE_FORMAT
        )


def import_modules(config):
    importer = Importer(config)
    importer.import_modules()

    if importer.error_handler_class is not None:
        importer.error_handler = importer.error_handler_class(config)

    return importer


def validate_config(config, server_parameters):
    if server_parameters.security_key is None:
        server_parameters.security_key = config.SECURITY_KEY

    if not isinstance(server_parameters.security_key, basestring):
        raise RuntimeError(
            'No security key was found for this instance of thumbor. ' +
            'Please provide one using the conf file or a security key file.')

    if config.USE_GIFSICLE_ENGINE:
        server_parameters.gifsicle_path = which('gifsicle')
        if server_parameters.gifsicle_path is None:
            raise RuntimeError(
                'If using USE_GIFSICLE_ENGINE configuration to True, the `gifsicle` binary must be in the PATH '
                'and must be an executable.'
            )


def get_application(context):
    return context.modules.importer.import_class(context.server.app_class)(context)


def run_server(application, context):
    server = HTTPServer(application)

    if context.server.fd is not None:
        fd_number = get_as_integer(context.server.fd)
        if fd_number is None:
            with open(context.server.fd, 'r') as sock:
                fd_number = sock.fileno()

        sock = socket.fromfd(fd_number,
                             socket.AF_INET | socket.AF_INET6,
                             socket.SOCK_STREAM)
        server.add_socket(sock)
    else:
        server.bind(context.server.port, context.server.ip)

    server.start(1)


def main(arguments=None):
    '''Runs thumbor server with the specified arguments.'''

    server_parameters = get_server_parameters(arguments)
    config = get_config(server_parameters.config_path)
    configure_log(config, server_parameters.log_level.upper())

    importer = import_modules(config)

    validate_config(config, server_parameters)

    context = Context(
        server=server_parameters,
        config=config,
        importer=importer
    )

    application = get_application(context)
    run_server(application, context)

    try:
        logging.debug('thumbor running at %s:%d' % (context.server.ip, context.server.port))
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- thumbor closed by user interruption --"
    finally:
        context.thread_pool.cleanup()

if __name__ == "__main__":
    main(sys.argv[1:])
