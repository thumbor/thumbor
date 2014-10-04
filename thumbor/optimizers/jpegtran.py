#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import os

from thumbor.optimizers import BaseOptimizer

class Optimizer(BaseOptimizer):

    def optimize(self, buffer, input_file, output_file):
        jpegtran_path = self.context.config.JPEGTRAN_PATH
        command = '%s -copy all -optimize -progressive -outfile %s %s ' % (
            jpegtran_path,
            output_file.name,
            input_file.name,
        )
        os.system(command)
