#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import thumbor_plugins.optimizers.gifv.Optimizer as GifvOptimizer

from thumbor.utils import logger


class Optimizer(GifvOptimizer):
    logger.warning("""
    This optimizer will be deprecated on the next major version.
    Add thumbor-plugins-gifv as a dependency, and
    change thumbor.optimizers.gifv to thumbor_plugins.optimizers.gifv
    on the OPTIMIZERS list on you thumbor.conf.
    """)