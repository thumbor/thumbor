#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from json import dumps

import tornado.gen

from thumbor.handlers import BaseHandler
from thumbor.lifecycle import Events


class Health(object):
    def __init__(self):
        self.healthy = True
        self.status = 200
        self.checks = {}

    def add_result(self, check_name, healthy, message):
        self.checks[check_name] = {
            'healthy': healthy,
            'message': message,
        }
        if not healthy:
            self.healthy = False
            self.status = 500


class HealthcheckHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        health = Health()
        yield Events.trigger(self, Events.Healthcheck.on_before_healthcheck, health=health)
        yield Events.trigger(self, Events.Healthcheck.on_healthcheck, health=health)
        yield Events.trigger(self, Events.Healthcheck.on_after_healthcheck, health=health)

        if health.healthy:
            self.write('WORKING')
        else:
            self.write(dumps(health.checks))

        self.set_status(health.status)

    def head(self, *args, **kwargs):
        self.set_status(200)


# In order to create healthcheck tests, just subscribe to the above events like this
# @tornado.gen.coroutine
# def test_health_trigger(sender, health):
    # health.add_result('bogus', False, 'testing')
    # return 'OK'


# Events.subscribe(Events.Healthcheck.on_healthcheck, test_health_trigger)
