#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import optparse

from thumbor.context import ServerParameters
from thumbor import __version__


def get_server_parameters(arguments=None):
    parser = optparse.OptionParser(usage="thumbor or type thumbor -h (--help) for help", description=__doc__, version=__version__)
    parser.add_option("-p", "--port", type="int", dest="port", default=8888, help="The port to run this thumbor instance at [default: %default].")
    parser.add_option("-i", "--ip", dest="ip", default="0.0.0.0", help="The host address to run this thumbor instance at [default: %default].")
    parser.add_option("-f", "--fd", dest="file_descriptor", help="The file descriptor number or path to listen for connections on (--port and --ip will be ignored if this is set) [default: %default].")
    parser.add_option("-c", "--conf", dest="conf", default="", help="The path of the configuration file to use for this thumbor instance [default: %default].")
    parser.add_option("-k", "--keyfile", dest="keyfile", default="", help="The path of the security key file to use for this thumbor instance [default: %default].")
    parser.add_option("-l", "--log-level", dest="log_level", default="warning", help="The log level to be used. Possible values are: debug, info, warning, error, critical or notset. [default: %default].")
    parser.add_option("-a", "--app", dest="app", default='thumbor.app.ThumborServiceApp', help="A custom app to use for this thumbor server in case you subclassed ThumborServiceApp [default: %default].")

    (options, args) = parser.parse_args(arguments)

    port = options.port
    ip = options.ip
    fd = options.file_descriptor
    conf = options.conf or None
    keyfile = options.keyfile or None
    log_level = options.log_level

    return ServerParameters(port=port,
                            ip=ip,
                            config_path=conf,
                            keyfile=keyfile,
                            log_level=log_level,
                            app_class=options.app,
                            fd=fd)
