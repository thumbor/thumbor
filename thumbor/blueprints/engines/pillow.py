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
    Events.subscribe(Events.Engine.draw_rectangle, on_draw_rectangle)
    Events.subscribe(Events.Engine.crop, on_crop)
    Events.subscribe(Events.Engine.flip_horizontally, on_flip_horizontally)
    Events.subscribe(Events.Engine.flip_vertically, on_flip_vertically)
    Events.subscribe(Events.Engine.reorientate, on_reorientate)
    Events.subscribe(Events.Engine.rotate, on_rotate)
    Events.subscribe(Events.Engine.serialize, on_serialize)

    Events.subscribe(Events.Engine.get_image_data_as_rgb, get_image_data_as_rgb)
    Events.subscribe(Events.Engine.convert_to_grayscale, convert_to_grayscale)
    Events.subscribe(Events.Engine.set_image_data, set_image_data)
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
def on_draw_rectangle(sender, details, left, top, width, height):  # pylint: disable=unused-argument
    'Handles the draw rectangle event'
    PillowExtensions.draw_rectangle(details, left, top, width, height)


@tornado.gen.coroutine
def on_crop(sender, details, left, top, right, bottom):  # pylint: disable=unused-argument,too-many-arguments
    'Handles the crop event'
    PillowExtensions.crop(details, left, top, right, bottom)


@tornado.gen.coroutine
def on_flip_horizontally(sender, details):  # pylint: disable=unused-argument,too-many-arguments
    'Handles the flip horizontally event'
    PillowExtensions.flip_horizontally(details)


@tornado.gen.coroutine
def on_flip_vertically(sender, details):  # pylint: disable=unused-argument,too-many-arguments
    'Handles the flip vertically event'
    PillowExtensions.flip_vertically(details)


@tornado.gen.coroutine
def on_reorientate(sender, details):  # pylint: disable=unused-argument
    'Handles the reorientate event'
    PillowExtensions.reorientate(details)

@tornado.gen.coroutine
def on_rotate(sender, details, degrees):  # pylint: disable=unused-argument
    'Handles the rotate event'
    PillowExtensions.rotate(details, degrees)


@tornado.gen.coroutine
def on_serialize(sender, details):  # pylint: disable=unused-argument
    'Serializes the image after transforming'
    PillowExtensions.serialize_image(details)


@tornado.gen.coroutine
def get_image_data_as_rgb(sender, details):  # pylint: disable=unused-argument
    'Gets the image mode and data as RGB buffer'
    return PillowExtensions.get_image_data_as_rgb(details)


@tornado.gen.coroutine
def convert_to_grayscale(sender, details, update_image, with_alpha):  # pylint: disable=unused-argument
    'Gets the image mode and data as RGB buffer'
    return PillowExtensions.convert_to_grayscale(details, update_image,
                                                 with_alpha)


@tornado.gen.coroutine
def set_image_data(sender, details, data):  # pylint: disable=unused-argument
    'Loads the image into PIL'
    return PillowExtensions.set_image_data(details, data)


@tornado.gen.coroutine
def get_image_size(sender, details):  # pylint: disable=unused-argument
    'Gets the image dimensions'
    return PillowExtensions.get_image_size(details)
