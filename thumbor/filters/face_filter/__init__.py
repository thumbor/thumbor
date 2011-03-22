#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, dirname, abspath
from cStringIO import StringIO

import cv
from PIL import Image
from tornado.options import define, options

from thumbor.filters import BaseFilter


define('FACE_FILTER_CASCADE_FILE', default='haarcascade_frontalface_alt.xml')


class Filter(BaseFilter):
    
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
        cascade = cv.Load(join(abspath(dirname(__file__)), options.FACE_FILTER_CASCADE_FILE))
        faces = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50))

        if faces:
            self.context['halign'], self.context['valign'] = DetectCrop(faces, size).get_crop()


class DetectCrop():
    def __init__(self, faces, size):
        self.faces = self.__normalize(faces)
        self.width = size[0]
        self.height = size[1]
        self.calculate_areas()

    def __normalize(self, faces):
        def normalize(face):
            face = face[0]
            face_height = face[1] + face[3]
            offset = int(face_height * 0.12)
            return (face[0], max(0, face[1] - offset), face[0] + face[2], face_height)
        return map(normalize, faces)

    def calculate_areas(self):
        self.areas = []
        area_width = self.width / 3.
        area_height = self.height / 3.
        for col in range(1,4):
            for row in range(1,4):
                self.areas.append((area_width * (row - 1), area_height * (col - 1), area_width * row, area_height * col))
    
    def get_crop(self):
        areas_weight = []

        for area in self.areas:
            total_weight = 0
            for face in self.faces:
                face_width = face[2] - face[0]
                face_height = face[3] - face[1]
                face_center_x = face[0] + face_width / 2.
                face_center_y = face[1] + face_height / 2.
                
                area_width = area[2] - area[0]
                area_height = area[3] - area[1]
                area_center_x = area[0] + area_width / 2.
                area_center_y = area[1] + area_height / 2.
                
                intersection_x = pow(max(0, pow(face_width/2. + area_width/2., 2) - pow(face_center_x - area_center_x, 2)), 2)
                intersection_y = pow(max(0, pow(face_height/2. + area_height/2., 2) - pow(face_center_y - area_center_y, 2)), 2)
                
                total_weight += intersection_x * intersection_y
            
            areas_weight.append(total_weight)

        top_weight = areas_weight[0] + areas_weight[1] + areas_weight[2]
        middle_weight = areas_weight[3] + areas_weight[4] + areas_weight[5]
        bottom_weight = areas_weight[6] + areas_weight[7] + areas_weight[8]
        vweights = [top_weight, middle_weight, bottom_weight]

        left_weight = areas_weight[0] + areas_weight[3] + areas_weight[6]
        center_weight = areas_weight[1] + areas_weight[4] + areas_weight[7]
        right_weight = areas_weight[2] + areas_weight[5] + areas_weight[8]
        hweights = [left_weight, center_weight, right_weight]

        valigns = ['top', 'middle', 'bottom']
        valign = valigns[vweights.index(max(vweights))]

        haligns = ['left', 'center', 'right']
        halign = haligns[hweights.index(max(hweights))]

        return halign, valign
