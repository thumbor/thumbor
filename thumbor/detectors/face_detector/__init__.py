#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Dict

from thumbor.detectors.local_detector import CascadeLoaderDetector

HAIR_OFFSET = 0.12


class Detector(CascadeLoaderDetector):
    def __init__(self, context, index, detectors):
        super().__init__(context, index, detectors)
        self.load_cascade_file(
            __file__, self.context.config.FACE_DETECTOR_CASCADE_FILE
        )

    def get_origin(self) -> str:
        return "Face Detection"

    def get_detection_offset(
        self, left: int, top: int, width: int, height: int
    ) -> Dict[str, int]:
        top_offset = -1 * height * HAIR_OFFSET

        if top - height * HAIR_OFFSET < 0.0:
            top_offset = 0.0

        return {"top": top_offset}
