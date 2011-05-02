#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web

from thumbor.handlers import BaseHandler

class MainHandler(BaseHandler):

    def initialize(self, loader, storage, engine, detectors, filters):
        self.loader = loader
        self.storage = storage
        self.engine = engine
        self.detectors = detectors
        self.filters = filters

    @tornado.web.asynchronous
    def get(self,
            meta,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom,
            fit_in,
            horizontal_flip,
            width,
            vertical_flip,
            height,
            halign,
            valign,
            smart,
            image,
            **kw):

        if not self.validate(image):
            self._error(404)
            return

        int_or_0 = lambda value: 0 if value is None else int(value)

        opt = {
            'meta': meta == 'meta',
            'crop': {
                'left': int_or_0(crop_left),
                'top': int_or_0(crop_top),
                'right': int_or_0(crop_right),
                'bottom': int_or_0(crop_bottom)
            },
            'fit_in': fit_in,
            'width': int_or_0(width),
            'height': int_or_0(height),
            'horizontal_flip': horizontal_flip == '-',
            'vertical_flip': vertical_flip == '-',
            'halign': halign or 'center',
            'valign': valign or 'middle',
            'smart': smart == 'smart'
        }

        return self.execute_image_operations(opt, image)

