#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import os
from os.path import dirname, exists
from uuid import uuid4
import hashlib
from shutil import move

import tornado.gen

from thumbor.lifecycle import Events


def plug_into_lifecycle():
    Events.subscribe(Events.Imaging.before_loading_source_image, on_before_loading_source_image)
    Events.subscribe(Events.Imaging.after_loading_source_image, on_after_loading_source_image)


def path_on_filesystem(path):
    digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
    return "%s/%s/%s" % (
        '/tmp/thumbor/storage',
        # self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'),
        digest[:2],
        digest[2:]
    )


def ensure_dir(path):
    if not exists(path):
        try:
            os.makedirs(path)
        except OSError as err:
            # FILE ALREADY EXISTS = 17
            if err.errno != 17:
                raise


@tornado.gen.coroutine
def on_before_loading_source_image(sender, request, details, request_parameters):
    file_abspath = path_on_filesystem(request_parameters.image_url)
    if not exists(file_abspath):
        return

    with open(file_abspath, 'rb') as f:
        details.source_image = f.read()


@tornado.gen.coroutine
def on_after_loading_source_image(sender, request, details, request_parameters):
    if details.source_image is None:
        return

    file_abspath = path_on_filesystem(request_parameters.image_url)
    temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-', ''))
    file_dir_abspath = dirname(file_abspath)

    # logger.debug('creating tempfile for %s in %s...' % (path, temp_abspath))

    ensure_dir(file_dir_abspath)

    with open(temp_abspath, 'wb') as _file:
        _file.write(details.source_image)

    # logger.debug('moving tempfile %s to %s...' % (temp_abspath, file_abspath))
    move(temp_abspath, file_abspath)

    return
