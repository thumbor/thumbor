#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging, logging.handlers, json
from thumbor import __version__

class ErrorHandler(object):
    def __init__(self, config):

        file = config.ERROR_FILE_LOGGER
        if not file:
            raise RuntimeError(
                "If you set USE_CUSTOM_ERROR_HANDLING to True, and you are using thumbor_file_logger.logger, " +
                "then you must specify the file path to log to with the ERROR_FILE_LOGGER configuration."
            )


        self.logger = logging.getLogger('error_handler')
        self.logger.setLevel(logging.ERROR)
        self.logger.addHandler(logging.handlers.WatchedFileHandler(config.ERROR_FILE_LOGGER))
            
    def handle_error(self, context, handler, exception):
        req = handler.request
        extra = {
            'thumbor-version': __version__
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
