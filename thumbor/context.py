#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, exists
import tornado
from concurrent.futures import ThreadPoolExecutor, Future
import functools

from thumbor.utils import logger
from thumbor.filters import FiltersFactory
from thumbor.metrics.logger_metrics import Metrics


class Context:
    '''
    Class responsible for containing:
    * Server Configuration Parameters (port, ip, key, etc);
    * Configurations read from config file (or defaults);
    * Importer with imported modules (engine, filters, detectors, etc);
    * Request Parameters (width, height, smart, meta, etc).

    Each instance of this class MUST be unique per request. This class should not be cached in the server.
    '''

    def __init__(self, server=None, config=None, importer=None, request_handler=None):
        self.server = server
        self.config = config
        if importer:
            self.modules = ContextImporter(self, importer)
            if importer.metrics:
                self.metrics = importer.metrics(config)
            else:
                self.metrics = Metrics(config)
        else:
            self.modules = None
            self.metrics = Metrics(config)

        self.app_class = 'thumbor.app.ThumborServiceApp'

        if hasattr(self.config, 'APP_CLASS'):
            self.app_class = self.config.APP_CLASS

        if hasattr(self.server, 'app_class') and self.server.app_class != 'thumbor.app.ThumborServiceApp':
            self.app_class = self.server.app_class

        self.filters_factory = FiltersFactory(self.modules.filters if self.modules else [])
        self.request_handler = request_handler
        self.statsd_client = self.metrics  # TODO statsd_client is deprecated, remove me on next minor version bump
        self.thread_pool = ThreadPool.instance(getattr(config, 'ENGINE_THREADPOOL_SIZE', 0))
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.modules:
            self.modules.cleanup()

        self.thread_pool.cleanup()


class ServerParameters(object):
    def __init__(self, port, ip, config_path, keyfile, log_level, app_class, debug=False, fd=None, gifsicle_path=None):
        self.port = port
        self.ip = ip
        self.config_path = config_path
        self.keyfile = keyfile
        self.log_level = log_level
        self.app_class = app_class
        self.debug = debug
        self._security_key = None
        self.fd = fd
        self.load_security_key()
        self.gifsicle_path = gifsicle_path

    @property
    def security_key(self):
        return self._security_key

    @security_key.setter
    def security_key(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        self._security_key = key

    def load_security_key(self):
        if not self.keyfile:
            return

        path = abspath(self.keyfile)
        if not exists(path):
            raise ValueError('Could not find security key file at %s. Please verify the keypath argument.' % path)

        with open(path, 'r') as f:
            security_key = f.read().strip()

        self.security_key = security_key


class RequestParameters:

    def __init__(self,
                 debug=False,
                 meta=False,
                 trim=None,
                 crop_left=None,
                 crop_top=None,
                 crop_right=None,
                 crop_bottom=None,
                 crop=None,
                 adaptive=False,
                 full=False,
                 fit_in=False,
                 width=0,
                 height=0,
                 horizontal_flip=False,
                 vertical_flip=False,
                 halign='center',
                 valign='middle',
                 filters=None,
                 smart=False,
                 quality=80,
                 image=None,
                 url=None,
                 extension=None,
                 buffer=None,
                 focal_points=None,
                 unsafe=False,
                 hash=None,
                 accepts_webp=False,
                 request=None,
                 max_age=None):

        self.debug = bool(debug)
        self.meta = bool(meta)
        self.trim = trim
        if trim is not None:
            trim_parts = trim.split(':')
            self.trim_pos = trim_parts[1] if len(trim_parts) > 1 else "top-left"
            self.trim_tolerance = int(trim_parts[2]) if len(trim_parts) > 2 else 0

        if crop is not None:
            self.crop = crop
        else:
            self.crop = {
                'left': self.int_or_0(crop_left),
                'right': self.int_or_0(crop_right),
                'top': self.int_or_0(crop_top),
                'bottom': self.int_or_0(crop_bottom)
            }

        self.should_crop = \
            self.crop['left'] > 0 or \
            self.crop['top'] > 0 or \
            self.crop['right'] > 0 or \
            self.crop['bottom'] > 0

        self.adaptive = bool(adaptive)
        self.full = bool(full)
        self.fit_in = bool(fit_in)

        self.width = width == "orig" and "orig" or self.int_or_0(width)
        self.height = height == "orig" and "orig" or self.int_or_0(height)
        self.horizontal_flip = bool(horizontal_flip)
        self.vertical_flip = bool(vertical_flip)
        self.halign = halign or 'center'
        self.valign = valign or 'middle'
        self.smart = bool(smart)

        if filters is None:
            filters = []

        self.filters = filters
        self.image_url = image
        self.url = url
        self.detection_error = None
        self.quality = quality
        self.buffer = None

        if focal_points is None:
            focal_points = []

        self.focal_points = focal_points
        self.hash = hash
        self.prevent_result_storage = False
        self.unsafe = unsafe == 'unsafe' or unsafe is True
        self.format = None
        self.accepts_webp = accepts_webp
        self.max_bytes = None
        self.max_age = max_age

        if request:
            self.url = request.path
            self.accepts_webp = 'image/webp' in request.headers.get('Accept', '')

    def int_or_0(self, value):
        return 0 if value is None else int(value)


class ContextImporter:
    def __init__(self, context, importer):
        self.context = context
        self.importer = importer

        self.engine = None
        if importer.engine:
            self.engine = importer.engine(context)

        self.gif_engine = None
        if importer.gif_engine:
            self.gif_engine = importer.gif_engine(context)

        self.storage = None
        if importer.storage:
            self.storage = importer.storage(context)

        self.result_storage = None
        if importer.result_storage:
            self.result_storage = importer.result_storage(context)

        self.upload_photo_storage = None
        if importer.upload_photo_storage:
            self.upload_photo_storage = importer.upload_photo_storage(context)

        self.loader = importer.loader
        self.detectors = importer.detectors
        self.filters = importer.filters
        self.optimizers = importer.optimizers
        self.url_signer = importer.url_signer

    def cleanup(self):
        if self.engine:
            self.engine.cleanup()


class ThreadPool(object):

    @classmethod
    def instance(cls, size):
        """
        Cache threadpool since context is
        recreated for each request
        """
        if not getattr(cls, "_instance", None):
            cls._instance = {}
        if size not in cls._instance:
            cls._instance[size] = ThreadPool(size)
        return cls._instance[size]

    def __init__(self, thread_pool_size):
        if thread_pool_size:
            self.pool = ThreadPoolExecutor(thread_pool_size)
        else:
            self.pool = None

    def _execute_in_foreground(self, operation, callback):
        result = Future()
        returned = None
        try:
            returned = operation()
        except Exception as e:
            # just log exception and release ioloop
            returned = e
            logger.exception(e)
        result.set_result(returned)
        callback(result)

    def _execute_in_pool(self, operation, callback):
        task = self.pool.submit(operation)
        task.add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                functools.partial(callback, future)
            )
        )

    def queue(self, operation, callback):
        if not self.pool:
            self._execute_in_foreground(operation, callback)
        else:
            self._execute_in_pool(operation, callback)

    def cleanup(self):
        if self.pool:
            print "Joining threads...."
            self.pool.shutdown()
