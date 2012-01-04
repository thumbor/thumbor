#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import traceback

import zmq
import bson

from detectors.face_detector import FaceDetector
from detectors.feature_detector import FeatureDetector
from detectors.glasses_detector import GlassesDetector
from detectors.profile_detector import ProfileDetector


HOST = "*"
PORT = 13337

class ImageProcessor:
    def __init__(self):
        self.detectors = {
            'face': FaceDetector(),
            'feat': FeatureDetector(),
            'glas': GlassesDetector(),
            'prof': ProfileDetector()
        }

    def detect(self, detector, size, mode, img_data):
        detector = self.detectors[detector]
        if detector is None:
            return None
        return detector.detect(size[0], size[1], mode, img_data)

if __name__ == "__main__":
    processor = ImageProcessor()

    context = zmq.Context()
    rep = context.socket(zmq.REP)
    rep.bind('tcp://%s:%s' % (HOST, PORT))
    while True:
        points = None
        msg = rep.recv()
        try:
            msg = bson.loads(msg)
            points = processor.detect(msg['type'], msg['size'], msg['mode'], msg['image'])
        except:
            traceback.print_exc()

        rep.send(bson.dumps({ 'points': points }))
