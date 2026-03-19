# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

"""This is the main module in thumbor"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("thumbor")
except PackageNotFoundError:
    __version__ = "0+unknown"
