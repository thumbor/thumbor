#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext
import tempfile

import tornado.web
from tornado.options import options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine
from thumbor.utils import logger
from thumbor.point import FocalPoint

CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png'
}

RCONTENT_TYPE = {}
for k,v in CONTENT_TYPE.iteritems():
    RCONTENT_TYPE[v] = k
    
class BaseHandler(tornado.web.RequestHandler):
    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            logger.error(msg)
        self.finish()

    def execute_image_operations(self, opt, image):

        should_crop = opt['crop']['left'] > 0 or \
                      opt['crop']['top'] > 0 or \
                      opt['crop']['right'] > 0 or \
                      opt['crop']['bottom'] > 0

        crop_left = crop_top = crop_right = crop_bottom = None
        if should_crop:
            crop_left = opt['crop']['left']
            crop_top = opt['crop']['top']
            crop_right = opt['crop']['right']
            crop_bottom = opt['crop']['bottom']

        width = opt['width']
        height = opt['height']

        if options.MAX_WIDTH and width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if options.MAX_HEIGHT and height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        halign = opt['halign']
        valign = opt['valign']

        extension = splitext(image)[-1].lower()

        self.get_image(opt['meta'], should_crop, crop_left,
                       crop_top, crop_right, crop_bottom,
                       opt['fit_in'],
                       opt['horizontal_flip'], width, opt['vertical_flip'],
                       height, halign, valign,
                       opt['smart'], image)

    def get_image(self,
                  meta,
                  should_crop,
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
                  should_be_smart,
                  image
                  ):
        def callback(buffer, mimetype):
            if buffer is None:
                self._error(404)
                return

            context = dict(
                loader=self.loader,
                engine=self.engine,
                storage=self.storage,
                buffer=buffer,
                should_crop=should_crop,
                crop_left=crop_left,
                crop_top=crop_top,
                crop_right=crop_right,
                crop_bottom=crop_bottom,
                fit_in=fit_in,
                should_flip_horizontal=horizontal_flip,
                width=width,
                should_flip_vertical=vertical_flip,
                height=height,
                halign=halign,
                valign=valign,
                focal_points=[]
            )

            extension = RCONTENT_TYPE[mimetype]
            self.engine.load(buffer, extension)

            if meta:
                context['engine'] = JSONEngine(self.engine, image)

            if self.detectors and should_be_smart:
                focal_points = self.storage.get_detector_data(image)
                if focal_points:
                    for point in focal_points:
                        context['focal_points'].append(FocalPoint.from_dict(point))
                else:
                    with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
                        jpg_buffer = buffer if extension in ('.jpg', '.jpeg') else self.engine.read('.jpg')
                        temp_file.write(jpg_buffer)
                        temp_file.seek(0)
                        context['file'] = temp_file.name
                        self.detectors[0](index=0, detectors=self.detectors).detect(context)

                    points = []
                    focal_points = context['focal_points']

                    for point in focal_points:
                        points.append(point.to_dict())

                    self.storage.put_detector_data(image, points)

            Transformer(context).transform()

            if meta:
                content_type = 'text/javascript' if options.META_CALLBACK_NAME else 'application/json'
            else:
                content_type = mimetype

            self.set_header('Content-Type', content_type)

            results = context['engine'].read(RCONTENT_TYPE[mimetype])

            self.write(results)
            self.finish()

        self._fetch(image, callback)

    def validate(self, path):
        if not hasattr(self.loader, 'validate'):
            return True

        is_valid = self.loader.validate(path)

        if not is_valid:
            logger.error('Request denied because the specified path "%s" was not identified by the loader as a valid path' % path)

        return is_valid

    def _fetch(self, url, callback):
        storage = self.storage
        buffer, mimetype = storage.get(url)

        if buffer is not None:
            callback(buffer, mimetype)
        else:
            def handle_loader_loaded(buffer, mimetype):
                if buffer is None:
                    callback(None, None)
                    return

                self.engine.load(buffer, RCONTENT_TYPE[mimetype])
                self.engine.normalize()
                buffer = self.engine.read()

                storage.put(url, buffer, mimetype)
                storage.put_crypto(url)

                callback(buffer, mimetype)

            self.loader.load(url, handle_loader_loaded)

class ContextHandler(BaseHandler):
    def initialize(self, loader, storage, engine, detectors, filters):
        self.loader = loader
        self.storage = storage.Storage()
        self.engine = engine.Engine()
        self.detectors = detectors
        self.filters = filters
