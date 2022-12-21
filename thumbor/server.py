#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging
import logging.config
import os
import sys
import warnings
from os.path import dirname, expanduser
from shutil import which
from socket import socket

import tornado.ioloop
from PIL import Image
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_unix_socket

from thumbor.config import Config
from thumbor.console import get_server_parameters
from thumbor.context import Context
from thumbor.importer import Importer
from thumbor.signal_handler import setup_signal_handler


def get_as_integer(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def get_config(config_path, use_environment=False):
    if use_environment:
        Config.allow_environment_variables()

    lookup_paths = [os.curdir, expanduser("~"), "/etc/", dirname(__file__)]

    return Config.load(
        config_path, conf_name="thumbor.conf", lookup_paths=lookup_paths
    )


def configure_log(config, log_level):
    if config.THUMBOR_LOG_CONFIG and config.THUMBOR_LOG_CONFIG != "":
        logging.config.dictConfig(config.THUMBOR_LOG_CONFIG)
    else:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=config.THUMBOR_LOG_FORMAT,
            datefmt=config.THUMBOR_LOG_DATE_FORMAT,
        )


def get_importer(config):
    importer = Importer(config)
    importer.import_modules()

    if importer.error_handler_class is not None:
        importer.error_handler = (
            importer.error_handler_class(  # pylint: disable=not-callable
                config
            )
        )

    return importer


def validate_config(config, server_parameters):
    if server_parameters.security_key is None:
        server_parameters.security_key = config.SECURITY_KEY

    if not isinstance(server_parameters.security_key, (bytes, str)):
        raise RuntimeError(
            "No security key was found for this instance of thumbor. "
            + "Please provide one using the conf file or a security key file."
        )

    if config.ENGINE or config.USE_GIFSICLE_ENGINE:
        # Error on Image.open when image pixel count is above MAX_IMAGE_PIXELS
        warnings.simplefilter("error", Image.DecompressionBombWarning)

    if config.USE_GIFSICLE_ENGINE:
        server_parameters.gifsicle_path = which("gifsicle")

        if server_parameters.gifsicle_path is None:
            raise RuntimeError(
                "If using USE_GIFSICLE_ENGINE configuration to True,"
                " the `gifsicle` binary must be in the PATH "
                "and must be an executable."
            )


def get_context(server_parameters, config, importer):
    return Context(server=server_parameters, config=config, importer=importer)


def get_application(context):
    return context.modules.importer.import_class(context.app_class)(context)


def get_socket_from_fd(fname_or_fd, *, non_blocking=False):
    fd_number = get_as_integer(fname_or_fd)

    if fd_number is not None:
        sock = socket(fileno=fd_number)
        if non_blocking:
            sock.setblocking(False)
    else:
        sock = bind_unix_socket(fname_or_fd)

    return sock


def run_server(application, context):
    server = HTTPServer(application, xheaders=True)

    if context.server.fd is not None:
        sock = get_socket_from_fd(
            context.server.fd,
            non_blocking=context.config.NON_BLOCKING_SOCKETS,
        )
        server.add_socket(sock)

        logging.debug("thumbor starting at fd %s", context.server.fd)
    else:
        server.bind(context.server.port, context.server.ip)

        logging.debug(
            "thumbor starting at %s:%d", context.server.ip, context.server.port
        )

    server.start(context.server.processes)

    return server


def main(arguments=None):
    """Runs thumbor server with the specified arguments."""

    if arguments is None:
        arguments = sys.argv[1:]

    server_parameters = get_server_parameters(arguments)
    config = get_config(
        server_parameters.config_path, server_parameters.use_environment
    )
    configure_log(config, server_parameters.log_level.upper())

    validate_config(config, server_parameters)

    importer = get_importer(config)

    with get_context(server_parameters, config, importer) as context:
        application = get_application(context)
        server = run_server(application, context)
        setup_signal_handler(server, config)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main(sys.argv[1:])
