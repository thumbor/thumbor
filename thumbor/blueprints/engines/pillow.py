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

from thumbor.blueprints.engines.pillow_extensions import PillowExtensions
from thumbor.lifecycle import Events


def plug_into_lifecycle():
    '''Plugs into thumbor's lifecycle'''
    Events.subscribe(Events.Engine.read_image, on_read_image)
    Events.subscribe(Events.Engine.resize, on_resize)
    Events.subscribe(Events.Engine.crop, on_crop)
    Events.subscribe(Events.Engine.reorientate, on_reorientate)
    Events.subscribe(Events.Engine.serialize, on_serialize)

    Events.subscribe(Events.Engine.get_image_data_as_rgb, get_image_data_as_rgb)
    Events.subscribe(Events.Engine.get_image_size, get_image_size)


@tornado.gen.coroutine
def on_read_image(sender, details, buffer):  # pylint: disable=unused-argument
    'Loads the image into PIL'
    PillowExtensions.read_image(details, buffer)


@tornado.gen.coroutine
def on_resize(sender, details, width, height):  # pylint: disable=unused-argument
    'Handles the resize event'
    PillowExtensions.resize(details, width, height)


@tornado.gen.coroutine
def on_crop(sender, details, left, top, right, bottom):  # pylint: disable=unused-argument,too-many-arguments
    'Handles the crop event'
    PillowExtensions.crop(details, left, top, right, bottom)


@tornado.gen.coroutine
def on_reorientate(sender, details):  # pylint: disable=unused-argument
    'Handles the reorientate event'
    PillowExtensions.reorientate(details)


@tornado.gen.coroutine
def on_serialize(sender, details):  # pylint: disable=unused-argument
    'Serializes the image after transforming'
    PillowExtensions.serialize_image(details)


@tornado.gen.coroutine
def get_image_data_as_rgb(sender, details):  # pylint: disable=unused-argument
    'Loads the image into PIL'
    return PillowExtensions.get_image_data_as_rgb(details)


@tornado.gen.coroutine
def get_image_size(sender, details):  # pylint: disable=unused-argument
    'Loads the image into PIL'
    return PillowExtensions.get_image_size(details)
