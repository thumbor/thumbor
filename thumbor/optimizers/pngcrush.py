#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os

from thumbor.optimizers import BaseOptimizer
from thumbor.utils import logger


class Optimizer(BaseOptimizer):
    def __init__(self, context):
        super(Optimizer, self).__init__(context)

        self.runnable = True
        self.pngcrush_path = self.context.config.PNGCRUSH_PATH
        if not (os.path.isfile(self.pngcrush_path) and os.access(self.pngcrush_path, os.X_OK)):
            logger.error("ERROR pngcrush path '{0}' is not accessible".format(self.pngcrush_path))
            self.runnable = False

    def should_run(self, image_extension, buffer):
        return 'png' in image_extension and self.runnable

    def optimize(self, buffer, input_file, output_file):
        command = '%s -reduce -q %s %s ' % (
            self.pngcrush_path,
            input_file,
            output_file,
        )
        os.system(command)
