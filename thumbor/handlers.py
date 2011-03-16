#!/usr/bin/env python
#-*- coding: utf8 -*-

import re
import urllib2
import cStringIO
from urlparse import urlparse
from os.path import join, splitext

from PIL import Image
import tornado.web
from tornado.options import define, options

from rect import BoundingRect

define('ALLOWED_DOMAINS', type=str, default=['globo.com'], multiple=True)
define('ALLOWED_SOURCES', type=str, default=['www.globo.com', 's.glbimg.com'], multiple=True)
define('MAX_WIDTH', type=int, default=1280)
define('MAX_HEIGHT', type=int, default=800)
define('QUALITY', type=int, default=80)

FORMATS = {
    '.jpg': "JPEG",
    '.jpeg': "JPEG",
    '.gif': "GIF",
    '.png': "PNG"
}

CONTENT_TYPE = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.png': 'image/png'
}

PROPORTION = 9999999999

class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):
    
    def _error(self, status, msg):
        self.set_status(status)
        self.write(msg)
        
    def _verify_allowed_domains(self):
        host = self.request.host.split(':')[0]
        for pattern in options.ALLOWED_DOMAINS:
            if re.match('^%s$' % pattern, host):
                return True
        return False

    def _verify_allowed_sources(self, url):
        res = urlparse(url)
        for pattern in options.ALLOWED_SOURCES:
            if re.match('^%s$' % pattern, res.hostname):
                return True
        return False

    def _fetch(self, url):
        response = urllib2.urlopen(url)
        return response.read()

    def _fetch_image(self, url):
        return Image.open(cStringIO.StringIO(self._fetch(url)))

    def _read_image(self, img, extension):
        img_buffer = cStringIO.StringIO()

        img.save(img_buffer, FORMATS[extension], quality=options.QUALITY)

        results = img_buffer.getvalue()

        img_buffer.close()

        return results

    def validate_url(self, url):
        
        url = join('http://', url)

        if not self._verify_allowed_domains():
            self._error(404, 'Your domain is not allowed!')
            return

        if not self._verify_allowed_sources(url):
            self._error(404, 'Your image source is not allowed!')
            return

        return url
    
    def transform(self, img, flip_horizontal, width, flip_vertical, height, image_format, halign="center", valign="middle"):
        img_width, img_height = img.size

        if not width and not height:
            width = img_width
            height = img_height

        if float(width) / float(img_width) > float(height) / float(img_height):
            new_height = img_height * width / img_width
            img = img.resize((width, new_height), Image.ANTIALIAS)
            image_width = width
            image_height = float(width) / float(img_width) * float(img_height)
        else:
            new_width = img_width * height / img_height
            img = img.resize((new_width, height), Image.ANTIALIAS)
            image_width = float(height) / float(img_height) * float(img_width)
            image_height = height

        rect = BoundingRect(height=image_height, width=image_width)
        rect.set_size(height=height, width=width, halign=halign, valign=valign)

        if not width:
            width = rect.target_width
        if not height:
            height = rect.target_height

        crop_dimensions = (
            rect.left * image_width,
            rect.top * image_height,
            rect.right * image_width,
            rect.bottom * image_height
        )

        img = img.crop(crop_dimensions)

        if flip_horizontal:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_vertical:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        img = img.resize((width, height))


        return img

    def get(self,
            flip_horizontal,
            width,
            flip_vertical,
            height,
            halign,
            valign,
            url):
        
        url = self.validate_url(url)

        if not url:
            return

        width = width and int(width) or 0
        height = height and int(height) or 0

        if width > options.MAX_WIDTH:
            width = options.MAX_WIDTH
        if height > options.MAX_HEIGHT:
            height = options.MAX_HEIGHT

        if not halign:
            halign = "center"
        if not valign:
            valign = "middle"

        extension = splitext(url)[-1]
        image_format = FORMATS[extension]

        img = self._fetch_image(url)

        img = self.transform(img, flip_horizontal, width, flip_vertical, height, image_format, halign, valign)

        results = self._read_image(img, extension)

        self.set_header('Content-Type', CONTENT_TYPE[extension])
        self.write(results)
    