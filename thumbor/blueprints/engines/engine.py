#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
'''
Thumbor engine. This class triggers events that should be implemented by each engine.

All methods are static coroutines.
'''

from tornado import gen

from thumbor.lifecycle import Events


class Engine(object):
    'Engine class. Triggers events captured by the engine blueprints.'

    @classmethod
    @gen.coroutine
    def resize(cls, sender, details, width=0, height=0):
        '''
        Triggers the resize event.
        '''
        yield Events.trigger(
            Events.Engine.before_resize,
            sender,
            details=details,
            width=width,
            height=height,
        )

        yield Events.trigger(
            Events.Engine.resize,
            sender,
            details=details,
            width=width,
            height=height,
        )

        yield Events.trigger(
            Events.Engine.after_resize,
            sender,
            details=details,
            width=width,
            height=height,
        )

    @classmethod
    @gen.coroutine
    def crop(cls, sender, details, left, top, right, bottom):  # pylint: disable=too-many-arguments
        '''
        Triggers the crop image event.
        '''
        yield Events.trigger(
            Events.Engine.before_crop,
            sender,
            details=details,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
        )

        yield Events.trigger(
            Events.Engine.crop,
            sender,
            details=details,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
        )

        yield Events.trigger(
            Events.Engine.after_crop,
            sender,
            details=details,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
        )
