#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor import __version__
from thumbor.error_handlers.file import ErrorHandler
from thumbor.config import Config
from thumbor.context import Context, ServerParameters

import json,tempfile


class FakeRequest(object):
    def __init__(self):
        self.headers = {
            'header1': 'value1',
            'Cookie': 'cookie1=value; cookie2=value2;'
        }

        self.url = "test/"
        self.method = "GET"
        self.arguments = []
        self.body = "body"
        self.query = "a=1&b=2"
        self.remote_ip = "127.0.0.1"

    def full_url(self):
        return "http://test/%s" % self.url


class FakeHandler(object):
    def __init__(self):
        self.request = FakeRequest()

@Vows.batch
class ErrorHandlerVows(Vows.Context):
    class WhenInvalidConfiguration(Vows.Context):
        def topic(self):
            cfg = Config()
            ErrorHandler(cfg)

        def should_be_error(self, topic):
            expect(topic).to_be_an_error()
            expect(topic).to_be_an_error_like(RuntimeError)

    class WhenErrorOccurs(Vows.Context):
        def topic(self):
            #use temporary file to store logs
            tmp = tempfile.NamedTemporaryFile(prefix='thumborTest.')

            cfg = Config(SECURITY_KEY='ACME-SEC', ERROR_FILE_LOGGER=tmp.name)
            server = ServerParameters(8889, 'localhost', 'thumbor.conf', None, 'info', None)
            server.security_key = 'ACME-SEC'
            ctx = Context(server, cfg, None)

            handler = ErrorHandler(cfg)
            http_handler = FakeHandler()

            handler.handle_error(ctx, http_handler, RuntimeError("Test"))
            #return content of file
            return tmp.read()
      
        def should_have_called_client(self, topic):
            #check against json version
            log = json.loads(topic)
            del log['extra']['timestamp']
            expect(log).to_be_like ({
                'Http': {
                    'url': 'http://test/test/',
                    'method': 'GET',
                    'data': [],
                    'body': "body",
                    'query_string': "a=1&b=2"
                },
                'interfaces.User': {
                    'ip': "127.0.0.1",
                },
                'exception': 'Test',
                'extra': {
                    'thumbor-version':  __version__,
                    'Headers' : {
                        'header1': 'value1', 
                        'Cookie': {
                            'cookie1': 'value', 
                            'cookie2': 'value2'
                        }
                    },
                }
            })

    class WhenErrorOccursiUSeContext(Vows.Context):
        def topic(self):
            port = 8890
            #use temporary file to store logs
            tmp = tempfile.NamedTemporaryFile(prefix='thumborTest.%i.' % port)

            cfg = Config(SECURITY_KEY='ACME-SEC', ERROR_FILE_LOGGER=tmp.name.replace('thumborTest.%i.' % port, 'thumborTest.%i.'), ERROR_FILE_NAME_USE_CONTEXT='server.port' )
            server = ServerParameters(port, 'localhost', 'thumbor.conf', None, 'info', None)
            server.security_key = 'ACME-SEC'
            ctx = Context(server, cfg, None)

            handler = ErrorHandler(cfg)
            http_handler = FakeHandler()

            handler.handle_error(ctx, http_handler, RuntimeError("Test"))
            #return content of file
            return tmp.read()

        def should_have_called_client(self, topic):
            #check against json version
            log = json.loads(topic)
            del log['extra']['timestamp']
            expect(log).to_be_like ({
                'Http': {
                    'url': 'http://test/test/',
                    'method': 'GET',
                    'data': [],
                    'body': "body",
                    'query_string': "a=1&b=2"
                },
                'interfaces.User': {
                    'ip': "127.0.0.1",
                },
                'exception': 'Test',
                'extra': {
                    'thumbor-version':  __version__,
                    'Headers' : {
                        'header1': 'value1',
                        'Cookie': {
                            'cookie1': 'value',
                            'cookie2': 'value2'
                        }
                    },
                }
            })

    class WhenInvalidConfigurationOfFileNameWithContext(Vows.Context):
        def topic(self):
            cfg = Config(ERROR_FILE_NAME_USE_CONTEXT='server..port', ERROR_FILE_LOGGER='toto')
            ErrorHandler(cfg)

        def should_be_error(self, topic):
            expect(topic).to_be_an_error()
            expect(topic).to_be_an_error_like(RuntimeError)

