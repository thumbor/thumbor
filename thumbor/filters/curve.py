#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import ast

from thumbor.ext.filters import _curve
from thumbor.filters import BaseFilter, filter_method

# pylint: disable=line-too-long


class Filter(BaseFilter):
    """
    Usage: /filters:curve(<curve of all channels>, <curve of R>, <curve o f G>, <curve of B>)
    Format of each curve : [(x1,y1),(x2,y2),...]
    Examples of use:
        /filters:curve([(0,0),(40,59),(255,255)],[(32,59),(64,80),(92,111),(128,153),(140,169),(164,201),(192,214),(224,215),(240,214),(255,212)],[(34,41),(64,51),(92,76),(128,112),(140,124),(164,147),(192,180),(224,216),(240,236),(255,255)],[(40,46),(64,55),(92,83),(128,127),(140,144),(164,174),(192,197),(224,199),(240,197),(255,198)])/
        /filters:curve([(0,0),(255,255)],[(0,50),(16,51),(32,69),(58,85),(92,120),(128,170),(140,186),(167,225),(192,245),(225,255),(244,255),(255,254)],[(0,0),(16,2),(32,18),(64,59),(92,116),(128,182),(167,211),(192,227),(224,240),(244,247),(255,252)],[(0,48),(16,50),(62,77),(92,110),(128,144),(140,153),(167,180),(192,192),(224,217),(244,225),(255,225)])/
    """  # NOQA

    regex = r"\[(?:\(\d+,\d+\),?)*\]"

    @filter_method(regex, regex, regex, regex)
    async def curve(self, alpha, red, green, blue):
        mode, data = self.engine.image_data_as_rgb()
        imgdata = _curve.apply(
            mode,
            data,
            tuple(ast.literal_eval(alpha)),
            tuple(ast.literal_eval(red)),
            tuple(ast.literal_eval(green)),
            tuple(ast.literal_eval(blue)),
        )
        self.engine.set_image_data(imgdata)
