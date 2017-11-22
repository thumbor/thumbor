#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'''
Thumbor request lifecycle events.

Thumbor's extensions should use these events to hook functionality.

All events are coroutines.

Example:

    from tornado import gen, ioloop
    from thumbor.lifecycle import Events

    @gen.coroutine
    def on_request_received_handler(sender, request):
        # do something
        return 'done'

    Events.subscribe(Events.Imaging.request_received, on_request_received_handler)
'''

import tornado.gen
from tornado import ioloop
from asyncblink import signal


class Events(object):
    '''Thumbor's request lifecycle events'''

    class Imaging(object):
        before_finish_request = signal('imaging.before_finish_request')
        after_finish_request = signal('imaging.after_finish_request')

        # Event executed before processing anything else
        request_received = signal('imaging.received')

        # Parsing Arguments Events
        before_parsing_arguments = signal('imaging.before_parsing_arguments')
        after_parsing_arguments = signal('imaging.after_parsing_arguments')

        # Source Image loading events
        before_loading_source_image = signal('imaging.before_loading_source_image')
        load_source_image = signal('imaging.loading_source_image')
        after_loading_source_image = signal('imaging.after_loading_source_image')
        source_image_not_found = signal('imaging.source_image_not_found')
        source_image_already_loaded = signal('imaging.source_image_already_loaded')

        # Image transformation events
        before_transforming_image = signal('imaging.before_transforming_image')
        image_transforming_phase_1 = signal('imaging.image_transforming_phase_1')
        image_transforming_phase_2 = signal('imaging.image_transforming_phase_2')
        image_transforming_phase_3 = signal('imaging.image_transforming_phase_3')
        image_transforming_phase_4 = signal('imaging.image_transforming_phase_4')
        image_transforming_phase_5 = signal('imaging.image_transforming_phase_5')
        after_transforming_image = signal('imaging.after_transforming_image')

    class Healthcheck(object):
        before_healthcheck = signal('healthcheck.before_healthcheck')
        healthcheck = signal('healthcheck.execute')
        after_healthcheck = signal('healthcheck.after_healthcheck')

    def __init__(self):
        raise RuntimeError('Events class should not be instantiated.')

    @staticmethod
    def scheduler(future):
        '''thumbor scheduler function. Use it in blinker.'''
        loop = ioloop.IOLoop.instance()
        loop.add_future(future, lambda f: f)
        return future

    @classmethod
    def get(cls, name):
        '''returns an event by name'''
        return signal(name)

    @classmethod
    @tornado.gen.coroutine
    def trigger(cls, event, sender, **kw):
        event_action = event.send(sender, **kw)
        if event_action:
            resp = yield event_action[0][1]
            return resp
        return None

    @classmethod
    def subscribe(cls, event, handler):
        event.connect(handler, scheduler=Events.scheduler)
