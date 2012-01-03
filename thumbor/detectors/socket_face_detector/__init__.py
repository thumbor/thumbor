#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import socket
from struct import *
from json import loads

from tornado import iostream
from tornado.options import options

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class Detector(BaseDetector):
    message_format = "4sII4s"

    def detect(self, context, callback):
        self.get_features(context, callback)

    def get_features(self, context, callback):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = iostream.IOStream(sock)
        engine = context['engine']

        def on_json(data):
            json_str = unpack('%ss' % len(data))
            features = loads(json_str)
            stream.close()

            if features:
                for (left, top, width, height) in features:
                    context['focal_points'].append(FocalPoint.from_square(left, top, width, height, origin="Face Detection"))
                    callback(context)
            else:
                self.next(context, callback)

        def on_result(data):
            size = unpack('I', data)
            stream.read_bytes(size, on_json)

        def send_request():
            image = engine.get_image_data()
            message = pack(self.message_format, "face", engine.size[0], engine.size[1], engine.get_image_mode())
            size_message = pack('I', len(message) + len(image))
            stream.write(size_message)
            stream.write(message)

            stream.read_bytes(4, on_result)


        self.stream.connect((options.OPENCV_SOCKET_ADDRESS, options.OPENCV_SOCKET_PORT), send_request)
