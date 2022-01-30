#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


import os
from tempfile import NamedTemporaryFile


class BaseOptimizer:
    def __init__(self, context):
        self.context = context

    def should_run(
        self, image_extension, image_buffer
    ):  # pylint: disable=unused-argument
        return True

    def run_optimizer(self, image_extension, buffer):
        if not self.should_run(image_extension, buffer):
            return buffer

        ifile = NamedTemporaryFile(  # pylint: disable=consider-using-with
            delete=False
        )
        ofile = NamedTemporaryFile(  # pylint: disable=consider-using-with
            delete=False
        )
        try:
            ifile.write(buffer)
            ifile.close()
            ofile.close()

            self.optimize(buffer, ifile.name, ofile.name)

            with open(
                ofile.name, "rb"
            ) as output_file:  # reopen with file thats been changed with the optimizer
                return output_file.read()
        finally:
            os.unlink(ifile.name)
            os.unlink(ofile.name)

    def optimize(self, image_buffer, input_file, output_file):
        raise NotImplementedError()
