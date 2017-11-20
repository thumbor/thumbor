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

       Events.on_request_received.connect(on_request_received_handler, scheduler=Events.scheduler)
'''

import tornado.gen
from tornado import ioloop
from asyncblink import signal


class Events(object):
    '''Thumbor's request lifecycle events'''

    class Imaging(object):
        # Event executed before processing anything else
        on_request_received = signal('request.received')

    class Healthcheck(object):
        on_before_healthcheck = signal('healthcheck.before_healthcheck')
        on_healthcheck = signal('healthcheck.execute')
        on_after_healthcheck = signal('healthcheck.after_healthcheck')

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
        return getattr(cls, name)

    @classmethod
    @tornado.gen.coroutine
    def trigger(cls, sender, event, **kw):
        event_action = event.send(sender, **kw)
        if event_action:
            resp = yield event_action[0][1]
            return resp
        return None

    @classmethod
    def subscribe(cls, event, handler):
        event.connect(handler, scheduler=Events.scheduler)
