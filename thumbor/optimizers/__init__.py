#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


import os
from tempfile import NamedTemporaryFile


class BaseOptimizer(object):
    def __init__(self, context):
        self.context = context

    def should_run(self, image_extension, buffer):
        return True

    def run_optimizer(self, image_extension, buffer):
        if not self.should_run(image_extension, buffer):
            return buffer

        with NamedTemporaryFile(delete=False) as input_file:
            try:
                with NamedTemporaryFile() as output_file:
                    input_file.write(buffer)
                    input_file.close()
                    self.optimize(buffer, input_file.name, output_file.name)
                    output_file.seek(0)
                    return output_file.read()
            finally:
                os.unlink(input_file.name)
