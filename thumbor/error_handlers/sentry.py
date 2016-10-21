#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import pkgutil
import pkg_resources

from thumbor import __version__


class ErrorHandler(object):
    def __init__(self, config, client=None):
        import raven

        dsn = config.SENTRY_DSN_URL
        if not dsn:
            raise RuntimeError(
                "If you set USE_CUSTOM_ERROR_HANDLING to True, and you are using thumbor.error_handlers.sentry, " +
                "then you must specify the Sentry DSN using the SENTRY_DSN_URL configuration."
            )

        self.sentry = client or raven.Client(dsn)
        self.modules = self.get_modules()

    def get_modules(self):
        resolved = {}
        for _, module, _ in pkgutil.iter_modules():
            try:
                res_mod = pkg_resources.get_distribution(module)
                if res_mod is not None:
                    resolved[module] = res_mod.version
            except Exception:
                pass

        return resolved

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
            'sentry.interfaces.Http': {
                'url': req.full_url(),
                'method': req.method,
                'data': req.arguments,
                'body': req.body,
                'query_string': req.query
            },
            'sentry.interfaces.User': {
                'ip': req.remote_ip,
            },
            'modules': self.modules
        }
        self.sentry.captureException(exception, extra=extra, data=data)
