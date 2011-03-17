#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import tempfile
from datetime import datetime
from tornado.options import options, define
from os.path import exists, dirname, join, getctime

define('FILE_STORAGE_ROOT_PATH', default=join(tempfile.gettempdir(), 'thumbor', 'storage'))

def _normalize_path(path):
    if path.startswith('/'):
        path = path[1:]
    
    return join(options.FILE_STORAGE_ROOT_PATH, path)

def put(path, bytes):
    file_abspath = _normalize_path(path)
    file_dir_abspath = dirname(file_abspath)
    
    if not exists(file_dir_abspath):
        os.makedirs(file_dir_abspath)
    
    with open(file_abspath, 'w') as _file:
        _file.write(bytes)

def get(path):
    file_abspath = _normalize_path(path)
    if not exists(file_abspath) or is_expired(file_abspath):
        return None
    return open(file_abspath, 'r').read()

def is_expired(path):
    timediff = datetime.now() - datetime.fromtimestamp(getctime(path))
    return timediff.seconds > options.STORAGE_EXPIRATION_SECONDS
