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

        ifile = NamedTemporaryFile(delete=False)
        ofile = NamedTemporaryFile(delete=False)
        try:
            ifile.write(buffer)
            ifile.close()
            ofile.close()

            self.optimize(buffer, ifile.name, ofile.name)

            ofile = open(ofile.name, 'rb')  # reopen with file thats been changed with the optimizer
            return ofile.read()

        finally:
            os.unlink(ifile.name)
            os.unlink(ofile.name)
