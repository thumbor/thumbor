#!/usr/bin/env python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath
from cStringIO import StringIO

from thumbor.detectors.face_detector import Detector as FaceDetector
from thumbor.detectors.glasses_detector import Detector as GlassesDetector
from transform_helper import MockEngine
from PIL import Image


__dirname = abspath(dirname(__file__))

def get_context_from(image, detectors):
    filename = join(__dirname, 'fixtures', 'img', image)
    buffer = open(filename).read()
    size = Image.open(StringIO(buffer)).size
    context = dict(
        engine=MockEngine(size),
        buffer=buffer,
        file=filename,
        focal_points=[]
    )
    detectors[0](index=0, detectors=detectors).detect(context)
    return context

def test_should_not_create_focal_points_on_images_that_has_no_face():
    focal_points = get_context_from('fixture1.png', [FaceDetector])['focal_points']
    assert len(focal_points) == 0

def test_should_return_detect_a_face():
    focal_points = get_context_from('face.jpg', [FaceDetector])['focal_points']
    assert len(focal_points) == 1
    assert focal_points[0].x == 96
    assert focal_points[0].y == 80.48
    assert focal_points[0].weight == 13689

def test_should_not_detect_glasses():
    focal_points = get_context_from('fixture1.png', [GlassesDetector])['focal_points']
    assert len(focal_points) == 0

def test_should_detect_glasses():
    focal_points = get_context_from('glasses.jpg', [GlassesDetector])['focal_points']
    assert len(focal_points) == 1



