#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import json

from tornado.options import options

from thumbor.engines import BaseEngine

class JSONEngine(BaseEngine):

    def __init__(self, engine, path):
        super(JSONEngine, self).__init__()
        self.engine = engine
        self.image = self.engine.image
        self.width, self.height = self.engine.size
        self.path = path
        self.operations = []

    def resize(self, width, height):
        self.operations.append({
            "type": "resize",
            "width": width,
            "height": height
        })

    def crop(self, left, top, right, bottom):
        self.operations.append({
            "type": "crop",
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom
        })

    def flip_vertically(self):
        self.operations.append({ "type": "flip_vertically" })

    def flip_horizontally(self):
        self.operations.append({ "type": "flip_horizontally" })

    def read(self, extension):
        return json.dumps({
            "thumbor": {
                "source": {
                    "url": self.path,
                    "width": self.width,
                    "height": self.height,
                },
                "operations": self.operations
            }
        })

