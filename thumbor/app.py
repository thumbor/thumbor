#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, abspath, dirname

import tornado.web
import tornado.ioloop
import tornado.options

from handlers import MainHandler


class ThumborServiceApp(tornado.web.Application):
    
    def __init__(self, conf_file=None):
        
        if conf_file is None:
            conf_file = abspath(join(dirname(__file__), 'conf.py'))
            
        tornado.options.parse_config_file(conf_file)

        handlers = [
            #(?:(\d+)x(\d+):(\d+)x(\d+)/)?
            (r'/(?:(-)?(\d+)?x(-)?(\d+)?/)?(?:(left|right|center)/)?(?:(top|bottom|middle)/)?/?(.+)', MainHandler),
        ]

        super(ThumborServiceApp, self).__init__(handlers)

application = ThumborServiceApp()

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    