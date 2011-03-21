#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
from os.path import splitext

import tornado.web
from tornado.options import define, options

from rect import BoundingRect

define('ALLOWED_DOMAINS', type=str, default=['localhost', '127.0.0.1', 'www.globo.com'], multiple=True)
define('MAX_WIDTH', type=int, default=1280)
define('MAX_HEIGHT', type=int, default=800)
define('QUALITY', type=int, default=80)

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
            self.write(msg)


class MainHandler(BaseHandler):
    
    def initialize(self, loader, storage, engine):
        self.loader = loader
        self.storage = storage
        self.engine = engine
    
    def _verify_allowed_domains(self):
        host = self.request.host.split(':')[0]
        for pattern in options.ALLOWED_DOMAINS:
            if re.match('^%s$' % pattern, host):
                return True
        return False

    def _fetch(self, url, callback):
        buffer = self.storage.get(url)

        if buffer is not None:
            callback(buffer)

        def _put_image(buffer):
            self.storage.put(url, buffer)
            callback(buffer)

        if not buffer:
            self.loader.load(url, _put_image)

    def validate(self, path):
        valid = self.loader.validate(path) if hasattr(self.loader, 'validate') else True
        return valid and self._verify_allowed_domains()

    def transform(self,
        should_crop, crop_left, crop_top, crop_right, crop_bottom,
        flip_horizontal, width, flip_vertical, height, halign, valign):
        
        if should_crop:
            self.engine.crop(crop_left, crop_top, crop_right, crop_bottom)
        
        img_width, img_height = self.engine.size

        if not width and not height:
            width = img_width
            height = img_height
        
        width = float(width)
        height = float(height)
        
        if width / img_width > height / img_height:
            new_height = img_height * width / img_width
            self.engine.resize(width, new_height)
            image_width = width
            image_height = width / img_width * img_height
        else:
            new_width = img_width * height / img_height
            self.engine.resize(new_width, height)
            image_width = height / img_height * img_width
            image_height = height

        rect = BoundingRect(image_width, image_height)
        rect.set_size(width, height, halign, valign)

        self.engine.crop(
            rect.left * image_width,
            rect.top * image_height,
            rect.right * image_width,
            rect.bottom * image_height
        )

        if flip_horizontal:
            self.engine.flip_horizontally()
        if flip_vertical:
            self.engine.flip_vertically()
            
        if not width:
            width = rect.target_width
        if not height:
            height = rect.target_height
            
        self.engine.resize(width, height)

    @tornado.web.asynchronous
    def get(self,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom,
            flip_horizontal,
            width,
            flip_vertical,
            height,
            halign,
            valign,
            path):

        if not self.validate(path):
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

        extension = splitext(path)[-1]

        def callback(buffer):
            self.engine.load(buffer)
            self.perform_transforms(
                should_crop, crop_left, crop_top, crop_right, crop_bottom,
                flip_horizontal, width, flip_vertical, height,
                halign, valign, extension
            )

        self._fetch(path, callback)

    def perform_transforms(self,
        should_crop, crop_left, crop_top, crop_right, crop_bottom,
        flip_horizontal, width, flip_vertical, height,
        halign, valign, extension):

        self.transform(should_crop, crop_left, crop_top, crop_right, crop_bottom, flip_horizontal, width, flip_vertical, height, halign, valign)
        results = self.engine.read(extension)
        self.set_header('Content-Type', CONTENT_TYPE[extension])
        self.write(results)
        self.finish()


class HealthcheckHandler(BaseHandler):
    def get(self):
        self.write('working')
