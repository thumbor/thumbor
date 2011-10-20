#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.crypto import Crypto
from thumbor.app import ThumborServiceApp

get_encrypted_url = lambda url, width, height, security_key='MY_SECURE_KEY': '/%s/%s' % (Crypto(security_key).encrypt(width, height, False, False, False, False, 'center', 'middle', None, None, None, None, url), url)

fixture_for = lambda path: abspath(join(dirname(__file__), 'fixtures', path))

image_url = 's.glbimg.com/jo/g1/f/original/2011/04/30/alabama1_ap620.jpg'

@Vows.batch
class CryptoHandlerVows(TornadoHTTPContext):
    def _get_app(self):
        application = ThumborServiceApp(fixture_for('encrypted_handler_conf.py'))
        application.loader.http_client = self._http_client
        return application

    class CryptoUrl(TornadoHTTPContext):

        class WhenInvalidDomain(TornadoHTTPContext):
            def topic(self):
                url = get_encrypted_url('ego.globo.com/Gente/foto/0,,48162393-EXH,00.jpg', 300, 200)

                self._http_client.fetch(self._get_url(url), self._stop)
                response = self._wait()

                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response[0]

                def should_be_an_error_code(self, topic):
                    expect(topic).to_equal(404)

            class Body(TornadoHTTPContext):
                def topic(self, response):
                    return response[1]

                def should_be_empty(self, topic):
                    expect(topic).to_be_empty()

        class WhenInvalidSecurityKey(TornadoHTTPContext):
            def topic(self):
                url = get_encrypted_url(image_url, 300, 200, 'fake-key')

                self._http_client.fetch(self._get_url(url), self._stop)
                response = self._wait()

                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response[0]

                def should_be_an_error_code(self, topic):
                    expect(topic).to_equal(404)

            class Body(TornadoHTTPContext):
                def topic(self, response):
                    return response[1]

                def should_be_empty(self, topic):
                    expect(topic).to_be_empty()

        class WhenInvalidUrl(TornadoHTTPContext):
            def topic(self):
                other_domain_image = "some.other.domain.com/image.jpg"
                url = get_encrypted_url(other_domain_image, 300, 200)

                self._http_client.fetch(self._get_url(url), self._stop)
                response = self._wait()

                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response[0]

                def should_be_an_error_code(self, topic):
                    expect(topic).to_equal(404)

            class Body(TornadoHTTPContext):
                def topic(self, response):
                    return response[1]

                def should_be_empty(self, topic):
                    expect(topic).to_be_empty()

        class WhenProperUrl(TornadoHTTPContext):
            def topic(self):
                response = self.get(get_encrypted_url(image_url, 300, 200))
                return (response.code, response.body)

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    if isinstance(response, (tuple, list)):
                        return response[0]
                    return response

                def should_not_be_an_error(self, topic):
                    expect(topic).to_equal(200)

            class Body(TornadoHTTPContext):
                def topic(self, response):
                    if isinstance(response, (tuple, list)):
                        return response[1]
                    return response

                def should_equal_image(self, topic):
                    expect(topic).not_to_be_an_error()
                    expect(topic).not_to_be_empty()

