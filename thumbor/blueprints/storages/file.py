#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'Blueprint for managing both storage and result storage in the file system.'

import os
from os.path import dirname, exists, abspath, getmtime
from uuid import uuid4
import hashlib
from shutil import move
from datetime import datetime

import pytz
import tornado.gen

from thumbor.lifecycle import Events


def plug_into_lifecycle():
    '''Plugs into thumbor's lifecycle of events'''
    Events.subscribe(Events.Imaging.after_parsing_arguments,
                     on_after_parsing_argument)
    Events.subscribe(Events.Imaging.after_finish_request,
                     on_after_finish_request)

    Events.subscribe(Events.Imaging.before_loading_source_image,
                     on_before_loading_source_image)
    Events.subscribe(Events.Imaging.after_loading_source_image,
                     on_after_loading_source_image)


def path_on_filesystem(path):
    '''Resolves the file in the filesystem'''
    digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
    return "%s/%s/%s" % (
        '/tmp/thumbor/storage',
        # self.context.config.FILE_STORAGE_ROOT_PATH.rstrip('/'),
        digest[:2],
        digest[2:])


def ensure_dir(path):
    'Ensures the directory exists'
    if not exists(path):
        try:
            os.makedirs(path)
        except OSError as err:
            # FILE ALREADY EXISTS = 17
            if err.errno != 17:
                raise


def validate_path(details, path):
    'Validates that the path starts with the root path'
    return abspath(path).startswith(
        details.config.RESULT_STORAGE_FILE_STORAGE_ROOT_PATH)


def is_expired(details, path):
    'Verifies if the file is expired'
    expire_in_seconds = details.config.get('RESULT_STORAGE_EXPIRATION_SECONDS',
                                           None)

    if expire_in_seconds is None or expire_in_seconds == 0:
        return False

    timediff = datetime.now() - datetime.fromtimestamp(getmtime(path))
    return timediff.seconds > expire_in_seconds


@tornado.gen.coroutine
def on_after_parsing_argument(sender, request, details):  # pylint: disable=unused-argument
    'Loads result storage from filesystem if it exists'
    request_parameters = details.request_parameters

    should_store = details.config.RESULT_STORAGE_STORES_UNSAFE or \
        not details.request_parameters.unsafe
    if not should_store:
        return

    file_abspath = path_on_filesystem(request_parameters.url)
    if not validate_path(details, file_abspath):
        return

    if not exists(file_abspath) or is_expired(details, file_abspath):
        return

    with open(file_abspath, 'rb') as result_file:
        details.transformed_image = result_file.read()

    details.headers['Last-Modified'] = datetime.fromtimestamp(
        getmtime(file_abspath)).replace(tzinfo=pytz.utc)


@tornado.gen.coroutine
def on_before_loading_source_image(sender, request, details):  # pylint: disable=unused-argument
    'Loads source image from filesystem if it exists'
    request_parameters = details.request_parameters
    file_abspath = path_on_filesystem(request_parameters.image_url)
    if not exists(file_abspath):
        return

    with open(file_abspath, 'rb') as source_file:
        details.source_image = source_file.read()


@tornado.gen.coroutine
def on_after_loading_source_image(sender, request, details):  # pylint: disable=unused-argument
    'Stores the source image in the filesystem'
    request_parameters = details.request_parameters
    if details.source_image is None:
        return

    file_abspath = path_on_filesystem(request_parameters.image_url)
    temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-', ''))
    file_dir_abspath = dirname(file_abspath)

    ensure_dir(file_dir_abspath)

    with open(temp_abspath, 'wb') as _file:
        _file.write(details.source_image)

    move(temp_abspath, file_abspath)

    return


@tornado.gen.coroutine
def on_after_finish_request(sender, request, details):  # pylint: disable=unused-argument
    'Stores the result image in the filesystem'
    request_parameters = details.request_parameters
    if details.status_code != 200 or details.transformed_image is None:
        return

    should_store = details.config.RESULT_STORAGE_STORES_UNSAFE or \
        not details.request_parameters.unsafe
    if not should_store:
        return

    file_abspath = path_on_filesystem(request_parameters.url)
    temp_abspath = "%s.%s" % (file_abspath, str(uuid4()).replace('-', ''))
    file_dir_abspath = dirname(file_abspath)

    ensure_dir(file_dir_abspath)

    with open(temp_abspath, 'wb') as _file:
        _file.write(details.transformed_image)

    move(temp_abspath, file_abspath)

    return
