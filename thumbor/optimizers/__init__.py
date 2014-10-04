#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


from tempfile import NamedTemporaryFile


class BaseOptimizer(object):
    def __init__(self, context):
        self.context = context

    def run_optimizer(self, buffer):
        with NamedTemporaryFile() as input_file:
            with NamedTemporaryFile() as output_file:
                input_file.write(buffer)
                self.optimize(buffer, input_file, output_file)
                output_file.seek(0)
                return output_file.read()
