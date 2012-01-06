#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.options import options
from pyremotecv import PyRemoteCV

from thumbor.detectors import BaseDetector


class RemoteDetector(BaseDetector):
    def detect(self, context, callback):
        engine = context['engine']
        host = 'tcp://%s:%s' % (options.REMOTECV_HOST, options.REMOTECV_PORT)
        image = engine.get_image_data()

        def on_result(points):
            result = []
            if not points: callback(result)

            for point in points:
                result.append(self.format_point(point))

            callback(result)

        PyRemoteCV.async_detect(
            action=self.detection_type,
            server=host,
            image_size=engine.size,
            image_bytes=image,
            image_mode=engine.get_image_mode(),
            callback=on_result,
            timeout=options.REMOTECV_TIMEOUT
        )

