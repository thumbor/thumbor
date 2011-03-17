#!/usr/bin/env python
#-*- coding: utf8 -*-

from os.path import join, abspath, dirname

import tornado.web
import tornado.ioloop
from tornado.options import define, options, parse_config_file

from handlers import MainHandler

define('LOADER', default='thumbor.loaders.http_loader')
define('STORAGE', default='thumbor.storages.file_storage')
define('STORAGE_EXPIRATION_SECONDS', type=int, default=60 * 60 * 24 * 30) # default one month

def real_import(name):
    if '.'  in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)

class ThumborServiceApp(tornado.web.Application):
    
    def __init__(self, conf_file=None):
        
        if conf_file is None:
            conf_file = abspath(join(dirname(__file__), 'conf.py'))
        parse_config_file(conf_file)

        loader = real_import(options.LOADER)
        storage = real_import(options.STORAGE)

        handlers = [
            #(?:(\d+)x(\d+):(\d+)x(\d+)/)?
            (r'/(?:(-)?(\d+)?x(-)?(\d+)?/)?(?:(left|right|center)/)?(?:(top|bottom|middle)/)?/?(.+)', MainHandler, {
                'loader': loader,
                'storage': storage
            }),
        ]

        super(ThumborServiceApp, self).__init__(handlers)

application = ThumborServiceApp()

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    