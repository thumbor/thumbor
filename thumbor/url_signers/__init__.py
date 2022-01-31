#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import importlib
import sys

# For backward compatibility
from libthumbor.url_signers import BaseUrlSigner  # NOQA

sys.modules[__name__] = importlib.import_module(
    "libthumbor.url_signers"
)  # NOQA
