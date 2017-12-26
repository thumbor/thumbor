#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'Server that runs thumbor and ties everything together'

import gc
import sys
from os.path import expanduser, dirname
import os
import logging
import logging.config
import warnings
import socket
import schedule

import tornado.ioloop
from tornado.httpserver import HTTPServer
from PIL import Image

from thumbor.console import get_server_parameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context
from thumbor.utils import which
from thumbor.lifecycle import Events


def get_as_integer(value):
    'Get value converted to integer or None'
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def get_config(config_path):
    'Load configuration'
    lookup_paths = [os.curdir, expanduser('~'), '/etc/', dirname(__file__)]

    return Config.load(
        config_path, conf_name='thumbor.conf', lookup_paths=lookup_paths)


def configure_log(config, log_level):
    '''Configure thumbor's log'''
    if (config.THUMBOR_LOG_CONFIG and config.THUMBOR_LOG_CONFIG != ''):
        logging.config.dictConfig(config.THUMBOR_LOG_CONFIG)
    else:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=config.THUMBOR_LOG_FORMAT,
            datefmt=config.THUMBOR_LOG_DATE_FORMAT)


def load_importer(config):
    'Load importer'
    importer = Importer(config)
    importer.import_modules()

    if importer.error_handler_class is not None:
        importer.error_handler = importer.error_handler_class(config)

    return importer


def validate_config(config, server_parameters):
    'Validates that the config file has all required parameters'
    if server_parameters.security_key is None:
        server_parameters.security_key = config.SECURITY_KEY

    if server_parameters.security_key is None:
        raise RuntimeError(
            'No security key was found for this instance of thumbor. ' +
            'Please provide one using the conf file or a security key file.')

    if config.ENGINE or config.USE_GIFSICLE_ENGINE:
        # Error on Image.open when image pixel count is above MAX_IMAGE_PIXELS
        warnings.simplefilter('error', Image.DecompressionBombWarning)

    if config.USE_GIFSICLE_ENGINE:
        server_parameters.gifsicle_path = which('gifsicle')
        if server_parameters.gifsicle_path is None:
            raise RuntimeError(
                'If using USE_GIFSICLE_ENGINE configuration to True, '
                'the `gifsicle` binary must be in the PATH '
                'and must be an executable.')


def get_context(server_parameters, config, importer):
    'Get a configured context'
    return Context(server=server_parameters, config=config, importer=importer)


def get_application(context):
    'Get the thumbor app'
    return context.modules.importer.import_class(context.app_class)(context)


def run_server(application, context):
    'Runs the server'
    server = HTTPServer(application, xheaders=True)

    if context.server.fd is not None:
        fd_number = get_as_integer(context.server.fd)
        if fd_number is None:
            with open(context.server.fd, 'r') as sock:
                fd_number = sock.fileno()

        sock = socket.fromfd(fd_number, socket.AF_INET | socket.AF_INET6,
                             socket.SOCK_STREAM)
        server.add_socket(sock)
    else:
        server.bind(context.server.port, context.server.ip)

    server.start(1)


def gc_collect():
    'Executes garbage collection'
    collected = gc.collect()
    if collected > 0:
        logging.info('Garbage collector: collected %d objects.', collected)


def bind_blueprints(importer):
    '''Binds blueprints to thumbor's lifcycle'''
    for blueprint in importer.blueprints:
        plug = getattr(blueprint, 'plug_into_lifecycle', None)
        if plug is not None:
            plug()


def main(arguments=None):
    '''Runs thumbor server with the specified arguments.'''
    if arguments is None:
        arguments = sys.argv[1:]

    event_args = {}

    Events.trigger_sync(Events.Server.before_server_parameters, None,
                        **event_args)
    server_parameters = get_server_parameters(arguments)
    event_args['server_parameters'] = server_parameters
    Events.trigger_sync(Events.Server.after_server_parameters, None,
                        **event_args)

    event_args['config_instance'] = Config
    Events.trigger_sync(Events.Server.before_config, None, **event_args)
    config = get_config(server_parameters.config_path)
    del event_args['config_instance']
    event_args['config'] = config
    Events.trigger_sync(Events.Server.after_config, None, **event_args)

    Events.trigger_sync(Events.Server.before_log_configuration, None,
                        **event_args)
    configure_log(config, server_parameters.log_level.upper())
    Events.trigger_sync(Events.Server.after_log_configuration, None,
                        **event_args)

    validate_config(config, server_parameters)

    Events.trigger_sync(Events.Server.before_importer, None, **event_args)
    importer = load_importer(config)
    event_args['importer'] = importer
    Events.trigger_sync(Events.Server.after_importer, None, **event_args)

    bind_blueprints(importer)

    with get_context(server_parameters, config, importer) as context:
        Events.trigger_sync(Events.Server.before_application_start, None,
                            **event_args)
        application = get_application(context)
        event_args['application'] = application
        Events.trigger_sync(Events.Server.after_application_start, None,
                            **event_args)

        Events.trigger_sync(Events.Server.before_server_run, None, **event_args)
        run_server(application, context)
        Events.trigger_sync(Events.Server.after_server_run, None, **event_args)

        if (config.GC_INTERVAL and config.GC_INTERVAL > 0):
            schedule.every(config.GC_INTERVAL).seconds.do(gc_collect)

        try:
            logging.debug('thumbor running at %s:%d', context.server.ip,
                          context.server.port)
            Events.trigger_sync(Events.Server.before_server_block, None,
                                **event_args)
            del event_args
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            sys.stdout.write("-- thumbor closed by user interruption --\n")


if __name__ == "__main__":
    main(sys.argv)
