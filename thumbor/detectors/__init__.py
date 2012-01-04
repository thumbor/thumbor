#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import join, dirname, abspath, isabs
import datetime

from tornado import iostream, ioloop, web
from tornado.options import options

import cv

import bson
import zmq
from zmq.eventloop import zmqstream

from thumbor.point import FocalPoint
from thumbor.utils import logger

class BaseDetector(object):

    def __init__(self, index, detectors):
        self.index = index
        self.detectors = detectors

    def detect(self, context, callback):
        raise NotImplementedError()

    def next(self, context, callback):
        if self.index >= len(self.detectors) - 1:
            callback()
            return

        next_detector = self.detectors[self.index + 1](self.index + 1, self.detectors)
        next_detector.detect(context, callback)

class RemoteDetector(BaseDetector):
    zmq_ctx = None

    def get_context(self):
        if RemoteDetector.zmq_ctx is None:
            RemoteDetector.zmq_ctx = zmq.Context()

        return RemoteDetector.zmq_ctx

    def detect(self, context, callback):
        self.context = context
        self.callback = callback
        self.ioloop = ioloop.IOLoop.instance()
        self.get_features()

    def on_result(self, data):
        self.ioloop.remove_timeout(self.timeout_handle)
        self.stream.close()
        features = bson.loads(data[0])['points']
        if features:
            for (left, top, width, height) in features:
                self.context['focal_points'].append(FocalPoint.from_square(left, top, width, height, origin="Face Detection"))
            self.callback()
        else:
            self.next(self.context, self.callback)

    def on_timeout(self):
        logger.warning('timeout for remote detector %s' % self.__class__.__module__)
        self.stream.close()
        self.context['detector_error'] = True
        self.callback()

    def get_features(self):
        engine = self.context['engine']
        image = engine.get_image_data()

        ctx = self.get_context()

        socket = ctx.socket(zmq.REQ)
        socket.connect('tcp://%s:%s' % (options.REMOTECV_HOST, options.REMOTECV_PORT))
        socket.setsockopt(zmq.LINGER, 0)

        self.timeout_handle = self.ioloop.add_timeout(datetime.timedelta(seconds=options.REMOTECV_TIMEOUT), self.on_timeout)
        self.stream = zmqstream.ZMQStream(socket, self.ioloop)
        self.stream.on_recv(self.on_result)

        self.stream.send(bson.dumps({ 'type': self.detection_type, 'size': engine.size, 'mode': engine.get_image_mode(), 'image': image }))


class CascadeLoaderDetector(BaseDetector):

    def load_cascade_file(self, module_path, cascade_file_path):
        if not hasattr(self.__class__, 'cascade'):
            if isabs(cascade_file_path):
                cascade_file = cascade_file_path
            else:
                cascade_file = join(abspath(dirname(module_path)), cascade_file_path)
            setattr(self.__class__, 'cascade', cv.Load(cascade_file))

    def get_min_size_for(self, size):
        ratio = int(min(size[0], size[1]) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    def get_features(self, context):
        engine = context['engine']
        sz = engine.size
        mode = engine.get_image_mode()
        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, engine.get_image_data())

        gray = cv.CreateImage(sz, 8, 1);
        convert_mode = getattr(cv, 'CV_%s2GRAY' % mode)
        cv.CvtColor(image, gray, convert_mode)

        # min_size = (20, 20)
        min_size = self.get_min_size_for(sz)
        haar_scale = 1.2
        min_neighbors = 1

        cv.EqualizeHist(gray, gray)

        faces = cv.HaarDetectObjects(gray,
                                     self.__class__.cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors,
                                     cv.CV_HAAR_DO_CANNY_PRUNING, min_size)

        #faces = cv.HaarDetectObjects(
            #image,
            #self.__class__.cascade,
            #cv.CreateMemStorage(0),
            #scale_factor=1.1,
            #min_neighbors=3,
            #flags=cv.CV_HAAR_DO_CANNY_PRUNING,
            #min_size=(40, 40)
        #)

        faces_scaled = []

        for ((x, y, w, h), n) in faces:
            # the input to cv.HaarDetectObjects was resized, so scale the
            # bounding box of each face and convert it to two CvPoints
            pt1 = (x, y)
            pt2 = ((x + w), (y + h))
            x1 = pt1[0]
            x2 = pt2[0]
            y1 = pt1[1]
            y2 = pt2[1]
            faces_scaled.append(((x1, y1, x2-x1, y2-y1), None))

        return faces_scaled

    def detect(self, context, callback):
        features = self.get_features(context)

        if features:
            for (left, top, width, height), neighbors in features:
                context['focal_points'].append(FocalPoint.from_square(left, top, width, height))
            callback()
        else:
            self.next(context, callback)

