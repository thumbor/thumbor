#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import json
import re
import time

from thumbor import __version__


class ErrorHandler(object):
    def __init__(self, config):
        if not config.ERROR_FILE_LOGGER:
            raise RuntimeError(
                "If you set USE_CUSTOM_ERROR_HANDLING to True, and you are using thumbor_file_logger.logger, " +
                "then you must specify the file path to log to with the ERROR_FILE_LOGGER configuration."
            )
        if (config.ERROR_FILE_NAME_USE_CONTEXT and not re.search('^(\w+\.)?\w+$', config.ERROR_FILE_NAME_USE_CONTEXT)):
            raise RuntimeError(
                "ERROR_FILE_NAME_USE_CONTEXT config must reffer an attribute of context "
                "object and be form of ^(\w+.)?\w+$ : %s" % config.ERROR_FILE_NAME_USE_CONTEXT
            )
        self.file_name = config.ERROR_FILE_LOGGER
        if config.ERROR_FILE_NAME_USE_CONTEXT:
            self.use_context = config.ERROR_FILE_NAME_USE_CONTEXT
        else:
            self.use_context = None
        self.logger = None

    def handle_error(self, context, handler, exception):
        # create log file if not existing
        if not self.logger:
            if self.use_context:
                if '.' in self.use_context:
                    parts = self.use_context.split('.')
                    obj = getattr(context, parts[0], None)
                    obj = reduce(getattr, parts[1:], obj)
                else:
                    obj = getattr(context, self.use_context, None)
                file = self.file_name % obj
            else:
                file = self.file_name

            self.logger = logging.getLogger('error_handler')
            self.logger.setLevel(logging.ERROR)
            self.logger.addHandler(logging.handlers.WatchedFileHandler(file))

        req = handler.request
        extra = {
            'thumbor-version': __version__,
            'timestamp': time.time()
        }
        extra.update({
            'Headers': req.headers
        })
        cookies_header = extra.get('Headers', {}).get('Cookie', {})
        if isinstance(cookies_header, basestring):
            cookies = {}
            for cookie in cookies_header.split(';'):
                if not cookie:
                    continue
                values = cookie.strip().split('=')
                key, val = values[0], "".join(values[1:])
                cookies[key] = val
        else:
            cookies = cookies_header
        extra['Headers']['Cookie'] = cookies

        data = {
            'Http': {
                'url': req.full_url(),
                'method': req.method,
                'data': req.arguments,
                'body': req.body,
                'query_string': req.query
            },
            'interfaces.User': {
                'ip': req.remote_ip,
            },
            'exception': str(exception),
            'extra': extra
        }

        self.logger.error(json.dumps(data))
