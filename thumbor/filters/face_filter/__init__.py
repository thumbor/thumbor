#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, dirname, abspath
from cStringIO import StringIO

import cv
from PIL import Image
from tornado.options import options

from thumbor.filters import BaseFilter

class Filter(BaseFilter):

    def __init__(self, context):
        super(Filter, self).__init__(context)
        self.cascade = cv.Load(join(abspath(dirname(__file__)), options.FACE_FILTER_CASCADE_FILE))

    def before(self):

        if not self.context['should_be_smart']:
            return

        size = self.context['engine'].size
        image_header = cv.CreateImageHeader(size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image_header, Image.open(StringIO(self.context['buffer'])).tostring())
        grayscale = cv.CreateImage(cv.GetSize(image_header), 8, 1)
        cv.CvtColor(image_header, grayscale, cv.CV_BGR2GRAY)
        storage = cv.CreateMemStorage(0)
        cv.EqualizeHist(grayscale, grayscale)
        faces = cv.HaarDetectObjects(grayscale, self.cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING)

        if faces:
            crop = DetectCrop(faces, size)
            self.context['halign'], self.context['valign'] = crop.alignments
        

class DetectCrop():
    def __init__(self, faces, size):
        self._center_of_mass = None
        self.faces = self.__normalize(faces)
        self.width = size[0]
        self.height = size[1]

    def __normalize(self, faces):
        def normalize(face):
            face = face[0]
            face_height = face[1] + face[3]
            # offset for the hair
            offset = int(face_height * 0.12)
            return (face[0], max(0, face[1] - offset), face[2], face[3])
        return map(normalize, faces)

    @property
    def center_of_mass(self):
        
        if self._center_of_mass:
            return self._center_of_mass
        
        def face_values(face):
            return face[0] + face[2] / 2., face[1] + face[3] / 2., face[2] * float(face[3])
            
        faces = map(face_values, self.faces)
        
        dividend_x = reduce(lambda total, face: total + (face[0] * face[2]), faces, 0)
        dividend_y = reduce(lambda total, face: total + (face[1] * face[2]), faces, 0)
        divisor = reduce(lambda total, face: total + face[2], faces, 0)
        
        x = dividend_x / divisor
        y = dividend_y / divisor
        
        self._center_of_mass = (x, y)
        
        return self._center_of_mass
    
    @property
    def alignments(self):
        x = self.center_of_mass[0]
        y = self.center_of_mass[1]
        return x / self.width, y / self.height
        
        
        