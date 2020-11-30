#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Project: PyCharm
# @File   : head_frame.py
# @Author : gaoyuan@infinities.com.cn
# @Time   : 2020/11/3 0003 18:00
import io

import tornado
from PIL import Image, ImageDraw
from thumbor.filters import BaseFilter, filter_method
from thumbor.utils import logger

try:
    # python2.x
    from urllib2 import urlopen, Request
except ImportError:
    # python3.x
    from urllib.request import urlopen, Request


class Filter(BaseFilter):
    @filter_method(
        BaseFilter.String,  # url
        BaseFilter.Number  # wm_diam
    )
    def head_frame(self, url, wm_diam):
        """
        url: The watermark request url
        wm_diam: Inner diameter of the watermark
        """
        # ensure the url is starts with http://
        if not url.startswith('http://'):
            url = 'http://%s' % url

        # get the request image
        head_img = self.engine.image
        head_img = head_img.convert('RGBA')
        # get size
        hd_w, hd_h = self.engine.size[0:]
        # ensure that the size of request image is fit with inner diameter of the watermark
        if min(hd_w, hd_h) != wm_diam:
            head_img = head_img.resize((wm_diam, wm_diam))

        # get the watermark image
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36", "Host": "www.foobar.com"}
            request = Request(url, headers=headers)
            img_bytes = urlopen(request, timeout=3).read()
        except Exception as e:
            logger.exception(e)
            logger.warn("bad watermark")
            raise tornado.web.HTTPError(500)

        # save watermark to buffer
        data_stream = io.BytesIO(img_bytes)

        # read from buffer
        wm_img = Image.open(data_stream)

        # ensure the watermark format is rgba
        wm_img = wm_img.convert('RGBA')

        # get watermark image size
        wm_w, wm_h = wm_img.size

        # calculate the padding
        p1 = (wm_w - wm_diam) // 2
        p2 = (wm_h - wm_diam) // 2

        # create a canvas filled with black
        base = Image.new('RGBA', (wm_w, wm_h), 0)

        # draw a circle filled with white 
        circle = Image.new('L', (wm_diam, wm_diam), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, wm_diam, wm_diam), fill=255)
        circle = circle.resize((wm_diam, wm_diam), Image.ANTIALIAS)

        # paste the white circle on the watermark image in order to get a circle head image
        head_img.putalpha(circle)

        # paste the new head image on the canvas
        base.paste(head_img, (p1, p2))

        # paste the watermark image on the canvas
        img_data = Image.alpha_composite(base, wm_img)

        # resize the new image
        img_data = img_data.resize(self.engine.size, Image.ANTIALIAS)

        # return to user
        self.engine.image = img_data

