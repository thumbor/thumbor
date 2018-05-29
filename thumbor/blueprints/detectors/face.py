#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import dirname, join
import tornado.gen as gen

from thumbor.lifecycle import Events
from thumbor.blueprints.detectors import get_features
from thumbor.point import FocalPoint

HAIR_OFFSET = 0.12
CASCADE_PATH = None


def plug_into_lifecycle():
    Events.subscribe(Events.Imaging.smart_detect, on_smart_detect)


def __add_hair_offset(top, height):
    top = max(0, top - height * HAIR_OFFSET)
    return top


@gen.coroutine
def on_smart_detect(sender, request, details):
    cascade_path = details.config.FACE_DETECTOR_CASCADE_FILE
    if cascade_path is None:
        cascade_path = join(
            dirname(__file__), 'haarcascade_frontalface_alt.xml')
    features = yield get_features(details, 'local-face-detect', cascade_path)

    if features:
        for (left, top, width, height), _ in features:
            top = __add_hair_offset(top, height)

            details.focal_points.append(
                FocalPoint.from_square(
                    left, top, width, height, origin='Face Detection'))
