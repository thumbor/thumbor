#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'''
Engine responsible for image operations using pillow.
'''

import tornado.gen

from thumbor.lifecycle import Events


def plug_into_lifecycle():
    Events.subscribe(Events.Imaging.before_transforming_image, on_before_transforming_image)


@tornado.gen.coroutine
def on_before_transforming_image(sender, request, details):
    if not details.has_filter('quality'):
        return
    quality = details.get_filter_arguments('quality')
    details.metadata['quality'] = quality
