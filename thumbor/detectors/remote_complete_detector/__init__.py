#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.detectors.remote_detector import RemoteDetector
from thumbor.point import FocalPoint

class Detector(RemoteDetector):
    detection_type = 'all'

    def format_point(self, point):
        if len(point) == 2:
            x, y = point
            return FocalPoint(x, y, 1, origin='Complete Detection').to_dict()
        else:
            left, top, width, height = point
            return FocalPoint.from_square(left, top, width, height, origin="Complete Detection").to_dict()
 
