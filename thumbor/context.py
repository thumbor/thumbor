#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, exists

class Context:
    '''
    Class responsible for containing:
    * Server Configuration Parameters (port, ip, key, etc);
    * Configurations read from config file (or defaults);
    * Importer with imported modules (engine, filters, detectors, etc);
    * Request Parameters (width, height, smart, meta, etc).

    Each instance of this class MUST be unique per request. This class should not be cached in the server.
    '''

    def __init__(self, server=None, config=None, importer=None):
        self.server = server
        self.config = config
        if importer:
            self.modules = ContextImporter(self, importer)
        else:
            self.modules = None


class ServerParameters:
    def __init__(self, port, ip, config_path, keyfile, log_level, app_class):
        self.port = port
        self.ip = ip
        self.config_path = config_path
        self.keyfile = keyfile
        self.log_level = log_level
        self.app_class = app_class
        self.security_key = None

    def load_security_key(self):
        if not self.keyfile: return

        path = abspath(self.keyfile)
        if not exists(path):
            raise ValueError('Could not find security key file at %s. Please verify the keypath argument.' % path)

        with open(path, 'r') as f:
            security_key = f.read().strip()

        self.security_key = security_key


class RequestParameters:
    def __init__(self,
                 debug,
                 meta,
                 crop,
                 fit_in,
                 width,
                 height,
                 horizontal_flip,
                 vertical_flip,
                 halign,
                 valign,
                 filters,
                 smart,
                 quality,
                 image_url,
                 extension=None,
                 buffer=None,
                 should_crop=False,
                 focal_points=[],
                 image_hash=None):
        self.debug = debug
        self.meta = meta
        self.crop = crop
        self.fit_in = fit_in
        self.width = width
        self.height = height
        self.horizontal_flip = horizontal_flip
        self.vertical_flip = vertical_flip
        self.halign = halign
        self.valign = valign
        self.smart = smart
        self.filters = filters
        self.image_url = image_url
        self.focal_points = []
        self.detection_error = None
        self.quality = quality
        self.buffer = None
        self.extension = extension
        self.should_crop = should_crop
        self.focal_points = focal_points
        self.image_hash = image_hash

class ContextImporter:
    def __init__(self, context, importer):
        self.context = context
        self.importer = importer

        self.engine = None
        if importer.engine:
            self.engine = importer.engine(context)

        self.storage = None
        if importer.storage:
            self.storage = importer.storage(context)

        self.loader = importer.loader
        self.detectors = importer.detectors
        self.filters = importer.filters

