#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import tornado.web

from thumbor.handlers import ContextHandler
from thumbor.context import RequestParameters

class MainHandler(ContextHandler):

    @tornado.web.asynchronous
    def get(self,
            debug,
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
            filters,
            image,
            **kw):

        if not self.validate(image):
            self._error(404)
            return

        int_or_0 = lambda value: 0 if value is None else int(value)

        opt = {
            'debug': debug == 'debug',
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
            'smart': smart == 'smart',
            'filters': filters or '',
            'image_url': image,
            'quality': self.context.config.QUALITY,
            'url': self.request.path
        }

        params = RequestParameters(**opt)
        self.context.request = params
        return self.execute_image_operations()

