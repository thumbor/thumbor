# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from thumbor.detectors import BaseDetector


class Detector(BaseDetector):
    async def detect(self):
        self.context.request.detection_error = True
