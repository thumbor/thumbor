#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath, isabs
from cStringIO import StringIO

import cv
from PIL import Image
from tornado.options import options, define

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


define('FACE_DETECTOR_CASCADE_FILE', default='haarcascade_frontalface_alt.xml')


HAIR_OFFSET = 0.12

class Detector(BaseDetector):
    
    def __init__(self, index, detectors):
        if not hasattr(Detector, 'cascade'):
            if isabs(options.FACE_DETECTOR_CASCADE_FILE):
                cascade_file = options.FACE_DETECTOR_CASCADE_FILE
            else:
                cascade_file = join(abspath(dirname(__file__)), options.FACE_DETECTOR_CASCADE_FILE)
            setattr(Detector, 'cascade', cv.Load(cascade_file))
        super(Detector, self).__init__(index, detectors)
    
    def __add_hair_offset(self, top, height):
        top = max(0, top - height * HAIR_OFFSET)
        return top
    
    def detect(self, context):
        size = context['engine'].size
        image_header = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image_header, Image.open(StringIO(context['buffer'])).tostring())
        
        grayscale = cv.CreateImage(size, 8, 1)
        cv.CvtColor(image_header, grayscale, cv.CV_BGR2GRAY)
        cv.EqualizeHist(grayscale, grayscale)
        faces = cv.HaarDetectObjects(grayscale, Detector.cascade, cv.CreateMemStorage(), 1.1, 3, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))

        if faces:
            for face in faces:
                left, top, width, height = face[0]
                top = self.__add_hair_offset(top, height)
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
        else:
            self.next(context)
        
        
