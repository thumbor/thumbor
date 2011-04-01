#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext
import hashlib

import tornado.web
from tornado.options import define, options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine
from thumbor.crypto import Crypto
from thumbor.utils import logger

define('MAX_WIDTH', type=int, default=1280)
define('MAX_HEIGHT', type=int, default=1024)
define('QUALITY', type=int, default=80)
define('SECURITY_KEY')

CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png'
}

class BaseHandler(tornado.web.RequestHandler):
    def _error(self, status, msg=None):
        self.set_status(status)
        if msg is not None:
            logger.error(msg)
        self.finish()

    def get_image(self,
                  meta,
                  should_crop,
                  crop_left,
                  crop_top,
                  crop_right,
                  crop_bottom,
                  horizontal_flip,
                  width,
                  vertical_flip,
                  height,
                  halign,
                  valign,
                  extension,
                  should_be_smart,
                  image
                  ):
        def callback(buffer):
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
                should_flip_horizontal=horizontal_flip,
                width=width,
                should_flip_vertical=vertical_flip,
                height=height,
                halign=halign,
                valign=valign,
                extension=extension,
                focal_points=[]
            )

            self.engine.load(buffer)

            if meta:
                context['engine'] = JSONEngine(self.engine, image)

            if self.detectors and should_be_smart:
                self.detectors[0](index=0, detectors=self.detectors).detect(context)

            Transformer(context).transform()

            if meta:
                self.set_header('Content-Type', "application/json")
            else:
                self.set_header('Content-Type', CONTENT_TYPE[context['extension']])

            results = context['engine'].read(context['extension'])

            self.write(results)
            self.finish()

        self._fetch(image, extension, callback)

    def validate(self, path):
        if not hasattr(self.loader, 'validate'):
            return True

        is_valid = self.loader.validate(path)

        if not is_valid:
            logger.error('Request denied because the specified path "%s" was not identified by the loader as a valid path' % path)

        return is_valid

    def _fetch(self, url, extension, callback):
        buffer = self.storage.get(url)

        if buffer is not None:
            callback(buffer)
        else:
            buffer = self.loader.load(url)
            if buffer is None:
                callback(None)
                return

            self.engine.load(buffer)
            self.engine.normalize()
            buffer = self.engine.read(extension)
            self.storage.put(url, buffer)
            callback(buffer)


class EncryptedHandler(BaseHandler):

    def initialize(self, loader, storage, engine, detectors):
        self.loader = loader
        self.storage = storage
        self.engine = engine
        self.detectors = detectors

    @tornado.web.asynchronous
    def get(self,
            crypto,
            image):

        try:
            cr = Crypto(options.SECURITY_KEY)
            opt = cr.decrypt(crypto)
        except TypeError:
            self._error(404, 'Request denied because the specified encrypted url "%s" could not be decripted' % crypto)
            return

        image_hash = opt and opt.get('image_hash')
        image_hash = image_hash[1:] if image_hash and image_hash.startswith('/') else image_hash
        path_hash = hashlib.md5(image).hexdigest()

        if not image_hash or image_hash != path_hash:
            self._error(404, 'Request denied because the specified image hash "%s" does not match the given image path hash "%s"' %(
                image_hash,
                path_hash
            ))
            return

        if not self.validate(image):
            self._error(404)
            return

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

        if width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        halign = opt['halign']
        valign = opt['valign']

        extension = splitext(image)[-1]

        self.get_image(opt['meta'], should_crop, crop_left,
                       crop_top, crop_right, crop_bottom,
                       opt['horizontal_flip'], width, opt['vertical_flip'],
                       height, halign, valign, extension,
                       opt['smart'], image)

class MainHandler(BaseHandler):

    def initialize(self, loader, storage, engine, detectors):
        self.loader = loader
        self.storage = storage
        self.engine = engine
        self.detectors = detectors

    @tornado.web.asynchronous
    def get(self,
            meta,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom,
            horizontal_flip,
            width,
            vertical_flip,
            height,
            halign,
            valign,
            smart,
            image):

        meta = meta == "meta"

        if not self.validate(image):
            self._error(404)
            return

        should_crop = crop_left is not None
        if should_crop:
            crop_left = int(crop_left)
            crop_top = int(crop_top)
            crop_right = int(crop_right)
            crop_bottom = int(crop_bottom)

        width = int(width) if width else 0
        height = int(height) if height else 0

        if width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        if not halign:
            halign = 'center'
        if not valign:
            valign = 'middle'

        extension = splitext(image)[-1]

        self.get_image(meta, should_crop, crop_left,
                       crop_top, crop_right, crop_bottom,
                       horizontal_flip, width, vertical_flip,
                       height, halign, valign, extension,
                       smart, image)
 
class HealthcheckHandler(BaseHandler):
    def get(self):
        self.write('working')

