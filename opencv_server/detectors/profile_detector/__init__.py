#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from detectors import CascadeLoaderDetector


class ProfileDetector(CascadeLoaderDetector):

    def __init__(self):
        self.load_cascade_file(__file__, 'haarcascade_profileface.xml')
