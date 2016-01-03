#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com


import os
from tempfile import NamedTemporaryFile


class BaseOptimizer(object):
    is_media_aware = False

    def __init__(self, context):
        self.context = context

    def should_run(self, media_or_image_extension, buffer=None):
        return True

    def run_optimizer(self, media):

        should_run = True
        if self.is_media_aware:
            should_run = self.should_run(media)
        else:
            should_run = self.should_run(
                media.metadata.get('FileExtension', ''),
                media.buffer
            )

        if not should_run:
            return False

        ifile = NamedTemporaryFile(delete=False)
        ofile = NamedTemporaryFile(delete=False)

        try:
            ifile.write(media.buffer)
            ifile.close()
            ofile.close()

            if self.is_media_aware:
                self.optimize(media, ifile.name, ofile.name)

                media.buffer = self._read_output_file(ofile)

                if not media.buffer:
                    media.is_valid = False
            else:
                self.optimize(media.buffer, ifile.name, ofile.name)
                return self._read_output_file(ofile)
        finally:
            os.unlink(ifile.name)
            os.unlink(ofile.name)

    def _read_output_file(self, output_file):
        buffer = None
        with open(output_file.name, 'rb') as result_file:
            buffer = result_file.read()
        return buffer
