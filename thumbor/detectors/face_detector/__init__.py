#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, dirname, abspath
from cStringIO import StringIO

import cv
from PIL import Image
from tornado.options import options

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint

HAIR_OFFSET = 0.12

class Detector(BaseDetector):
    
    def __init__(self, index, detectors):
        if not hasattr(Detector, 'cascade'):
            setattr(Detector, 'cascade', cv.Load(join(abspath(dirname(__file__)), options.FACE_FILTER_CASCADE_FILE)))
        super(Detector, self).__init__(index, detectors)
    
    def __add_hair_offset(self, top, height):
        top = max(0, top - height * HAIR_OFFSET)
        return top
    
    def detect(self, context):

        if not context['should_be_smart']:
            return

        size = context['engine'].size
        image_header = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image_header, Image.open(StringIO(context['buffer'])).tostring())
        grayscale = cv.CreateImage(size, 8, 1)
        cv.CvtColor(image_header, grayscale, cv.CV_BGR2GRAY)
        cv.EqualizeHist(grayscale, grayscale)
        faces = cv.HaarDetectObjects(grayscale, Detector.cascade, cv.CreateMemStorage(), 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING)

        if faces:
            for face in faces:
                left, top, width, height = face[0]
                top = self.__add_hair_offset(top, height)
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
        else:
            self.next(context)
        
        