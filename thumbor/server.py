#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import logging

import tornado.ioloop
from tornado.httpserver import HTTPServer
#from pyremotecv import tornado_extensions
#tornado_extensions.install_io_loop()

from thumbor.app import ThumborServiceApp
from thumbor.console import get_server_parameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context


def main(arguments=None):
    '''Runs thumbor server with the specified arguments.'''

    server_parameters = get_server_parameters(arguments)
    logging.basicConfig(level=getattr(logging, server_parameters.log_level.upper()))
    config = Config.load(server_parameters.config_path)
    importer = Importer(config)
    importer.import_modules()

    if not server_parameters.security_key is None:
        if config.SECURITY_KEY:
            server_parameters.security_key = config.SECURITY_KEY
        else:
            raise RuntimeError('No security key was found for this instance of thumbor. Please provide one using the conf file or a security key file.')

    context = Context(server=server_parameters, config=config, importer=importer)
    application = ThumborServiceApp(context)

    server = HTTPServer(application)
    server.bind(context.server.port, context.server.ip)
    server.start(1)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print "-- thumbor closed by user interruption --"

if __name__ == "__main__":
    main(sys.argv[1:])
