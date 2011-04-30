#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import splitext
import hashlib
import tempfile

import tornado.web
from tornado.options import options

from thumbor.transformer import Transformer
from thumbor.engines.json_engine import JSONEngine
from thumbor.crypto import Crypto
from thumbor.utils import logger

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
                       height, halign, valign, extension,
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
                fit_in=fit_in,
                should_flip_horizontal=horizontal_flip,
                width=width,
                should_flip_vertical=vertical_flip,
                height=height,
                halign=halign,
                valign=valign,
                extension=extension,
                focal_points=[]
            )

            self.engine.load(buffer, extension)

            if meta:
                context['engine'] = JSONEngine(self.engine, image)

            if self.detectors and should_be_smart:
                with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
                    jpg_buffer = buffer if extension in ('.jpg', '.jpeg') else self.engine.read('.jpg')
                    temp_file.write(jpg_buffer)
                    temp_file.seek(0)
                    context['file'] = temp_file.name
                    self.detectors[0](index=0, detectors=self.detectors).detect(context)

            Transformer(context).transform()

            content_type = "application/json" if meta else CONTENT_TYPE[context['extension']]
            self.set_header('Content-Type', content_type)

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
            def handle_loader_loaded(buffer):
                if buffer is None:
                    callback(None)
                    return

                self.engine.load(buffer, extension)
                self.engine.normalize()
                buffer = self.engine.read()
                self.storage.put(url, buffer)
                callback(buffer)
            self.loader.load(url, handle_loader_loaded)

class EncryptedHandler(BaseHandler):

    def initialize(self, loader, storage, engine, detectors, filters):
        self.loader = loader
        self.storage = storage
        self.engine = engine
        self.detectors = detectors
        self.filters = filters

    @tornado.web.asynchronous
    def get(self,
            crypto,
            image,
            security_key=None,
            **kw):

        if not security_key and options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            security_key = self.storage.get_crypto(image)

        try:
            cr = Crypto(security_key or options.SECURITY_KEY)
            opt = cr.decrypt(crypto)
        except TypeError:
            self._error(404, 'Request denied because the specified encrypted url "%s" could not be decripted' % crypto)
            return

        image_hash = opt and opt.get('image_hash')
        image_hash = image_hash[1:] if image_hash and image_hash.startswith('/') else image_hash
        path_hash = hashlib.md5(image).hexdigest()

        if not image_hash or image_hash != path_hash:
            self._error(404, 'Request denied because the specified image hash "%s" does not match the given image path hash "%s"' %(
                unicode(image_hash, errors='replace'),
                path_hash
            ))
            return

        if not self.validate(image):
            self._error(404)
            return

        return self.execute_image_operations(opt, image)

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

class HealthcheckHandler(BaseHandler):
    def get(self):
        self.write('working')

