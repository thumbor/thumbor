#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import argparse

from thumbor import __release_date__, __version__
from thumbor.context import ServerParameters


def get_server_parameters(arguments=None):
    if arguments is None:
        arguments = []

    parser = argparse.ArgumentParser(description="thumbor server")

    parser.add_argument(
        "--version",
        action="version",
        version=f"Thumbor v{__version__} ({__release_date__})",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=8888,
        type=int,
        help="The port to run this thumbor instance at [default: %(default)s].",
    )

    parser.add_argument(
        "-i",
        "--ip",
        default="0.0.0.0",
        help="The host address to run this thumbor instance at [default: %(default)s].",
    )

    parser.add_argument(
        "-f",
        "--fd",
        help="The file descriptor number or path to unix socket to listen for connections "
        "on (--port and --ip will be ignored if this is set)"
        "[default: %(default)s].",
    )

    parser.add_argument(
        "-c",
        "--conf",
        default=None,
        help="The path of the configuration file to use for this "
        "thumbor instance [default: %(default)s].",
    )

    parser.add_argument(
        "-k",
        "--keyfile",
        default=None,
        help="The path of the configuration file to use for this "
        "thumbor instance [default: %(default)s].",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        default="warning",
        help="The log level to be used. Possible values are: "
        "debug, info, warning, error, critical or notset. "
        "[default: %(default)s].",
    )

    parser.add_argument(
        "-a",
        "--app",
        default="thumbor.app.ThumborServiceApp",
        help="A custom app to use for this thumbor server in case "
        "you subclassed ThumborServiceApp [default: %(default)s].",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Debug mode [default: %(default)s].",
    )

    parser.add_argument(
        "--use-environment",
        default=False,
        help="Use environment variables for config",
    )

    parser.add_argument(
        "--processes",
        default=1,
        type=int,
        help="Number of processes to run. By default 1 and means no forks created"
        "Set to 0 to detect the number of cores available on this machine"
        "Set > 1 to start that specified number of processes"
        "[default: %(default)s].",
    )

    options = parser.parse_args(arguments)

    return ServerParameters(
        port=options.port,
        ip=options.ip,
        config_path=options.conf,
        keyfile=options.keyfile,
        log_level=options.log_level,
        app_class=options.app,
        debug=options.debug,
        fd=options.fd,
        use_environment=options.use_environment,
        processes=options.processes,
    )
