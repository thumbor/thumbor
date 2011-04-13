#!/usr/bin/env python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath
from cStringIO import StringIO

from thumbor.detectors.face_detector import Detector
from transform_helper import MockEngine
from PIL import Image


__dirname = abspath(dirname(__file__))

def get_context_from(image):
    buffer = open(join(__dirname, 'fixtures', 'img', image)).read()
    size = Image.open(StringIO(buffer)).size
    context = dict(
        engine=MockEngine(size),
        buffer=buffer,
        focal_points=[]
    )
    Detector(index=0, detectors=[Detector]).detect(context)
    return context

def test_should_not_create_focal_points_on_images_that_has_no_face():
    focal_points = get_context_from('fixture1.png')['focal_points']
    assert len(focal_points) == 0

def test_should_return_1_focal_point_on_images_with_1_face():
    focal_points = get_context_from('face.jpg')['focal_points']
    assert len(focal_points) == 1
    assert focal_points[0].x == 95
    assert focal_points[0].y == 79.6
    assert focal_points[0].weight == 13225
