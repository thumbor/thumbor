#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import logging
import os
import socket
from os.path import expanduser, dirname

import tornado.ioloop
from tornado.httpserver import HTTPServer

from thumbor.console import get_server_parameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context


def get_as_integer(value):
    try:
        return int(value)
    except ValueError:
        return None

def main(arguments=None):
    '''Runs thumbor server with the specified arguments.'''

    server_parameters = get_server_parameters(arguments)

    lookup_paths = [os.curdir,
                    expanduser('~'),
                    '/etc/',
                    dirname(__file__)]

    config = Config.load(server_parameters.config_path, conf_name='thumbor.conf', lookup_paths=lookup_paths)

    logging.basicConfig(
        level=getattr(logging, server_parameters.log_level.upper()),
        format=config.THUMBOR_LOG_FORMAT,
        datefmt=config.THUMBOR_LOG_DATE_FORMAT
    )

    importer = Importer(config)
    importer.import_modules()

    if importer.error_handler_class is not None:
        importer.error_handler = importer.error_handler_class(config)

    if server_parameters.security_key is None:
        server_parameters.security_key = config.SECURITY_KEY

    if not isinstance(server_parameters.security_key, basestring):
        raise RuntimeError(
            'No security key was found for this instance of thumbor. ' +
            'Please provide one using the conf file or a security key file.')

    context = Context(server=server_parameters, config=config, importer=importer)

    application = importer.import_class(server_parameters.app_class)(context)

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

    try:
        logging.debug('thumbor running at %s:%d' % (context.server.ip, context.server.port))
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- thumbor closed by user interruption --"

if __name__ == "__main__":
    main(sys.argv[1:])
