#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
from os.path import splitext

import tornado.web
from tornado.options import define, options

from rect import BoundingRect

define('ALLOWED_DOMAINS', type=str, default=['localhost', 'www.globo.com'], multiple=True)
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

    def _fetch(self, url):
        loader_resolve = getattr(self.loader, 'resolve', lambda _path: _path)
        resolved_url = loader_resolve(url)
        buffer = self.storage.get(resolved_url)

        if not buffer:
            buffer = self.loader.load(url)
            self.storage.put(resolved_url, buffer)

        return buffer

    def _fetch_image(self, url):
        self.engine.load(self._fetch(url))

    def validate(self, path):
        return self._verify_allowed_domains() and getattr(self.loader, 'validate', lambda _path: True)(path)

    def transform(self, flip_horizontal, width, flip_vertical, height, halign, valign):
        img_width, img_height = self.engine.size

        if not width and not height:
            width = img_width
            height = img_height

        if float(width) / float(img_width) > float(height) / float(img_height):
            new_height = img_height * width / img_width
            self.engine.resize(width, new_height)
            image_width = width
            image_height = float(width) / float(img_width) * float(img_height)
        else:
            new_width = img_width * height / img_height
            self.engine.resize(new_width, height)
            image_width = float(height) / float(img_height) * float(img_width)
            image_height = height

        rect = BoundingRect(height=image_height, width=image_width)
        rect.set_size(height=height, width=width, halign=halign, valign=valign)

        if not width:
            width = rect.target_width
        if not height:
            height = rect.target_height

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

        self.engine.resize(width, height)

    @tornado.web.asynchronous
    def get(self,
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

        self._fetch_image(path)

        self.transform(flip_horizontal, width, flip_vertical, height, halign, valign)

        results = self.engine.read(extension)

        self.set_header('Content-Type', CONTENT_TYPE[extension])

        self.write(results)
        self.finish()
    