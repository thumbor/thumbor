#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, exists, isabs

import cv2
import numpy as np
import tornado.gen as gen

from thumbor import Engine
from thumbor.point import FocalPoint


class CascadeRegistry:
    _instance = None

    def __init__(self):
        self.cascades = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = CascadeRegistry()

        return cls._instance

    def get_cascade(self, key, cascade_file_path):
        if key not in self.cascades:
            self.cascades[key] = load_cascade_file(cascade_file_path)

        return self.cascades[key]


def load_cascade_file(cascade_file_path):
    cascade_file = cascade_file_path

    if not isabs(cascade_file_path):
        cascade_file = abspath(cascade_file_path)

    if not exists(cascade_file):
        raise RuntimeError(f"Cascade file {cascade_file} could not be found.")

    return cv2.CascadeClassifier(cascade_file)


def get_min_size_for(size):
    ratio = int(min(size) / 15)
    ratio = max(20, ratio)

    return (ratio, ratio)


async def get_features(details, key, cascade_file_path):
    cascade = CascadeRegistry.instance().get_cascade(key, cascade_file_path)
    img = await Engine.convert_to_grayscale(
        "detectors", details, update_image=False, with_alpha=False
    )
    img = np.array(img)
    size = await Engine.get_image_size("detectors", details)

    faces = cascade.detectMultiScale(img, 1.2, 4, minSize=get_min_size_for(size))
    faces_scaled = []

    for (pos_x, pos_y, width, height) in faces:
        faces_scaled.append(
            ((pos_x.item(), pos_y.item(), width.item(), height.item()), 0)
        )

    return faces_scaled
