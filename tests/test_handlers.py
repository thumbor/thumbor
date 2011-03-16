#!/usr/bin/env python
#-*- coding: utf8 -*-

import unittest
import sys
from os.path import join, abspath, dirname

sys.path.append(abspath(join(dirname(__file__), '..')))

from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp

get_conf_path = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MainHandlerDomainTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return ThumborServiceApp(get_conf_path('conf.py'))

    def test_validates_passed_url_is_in_valid_domains(self):
        self.http_client.fetch(self.get_url('/www.mydomain.com/logo1.jpg'), self.stop)
        response = self.wait()
        self.assertEqual(404, response.code)
        self.assertEqual('Your domain is not allowed!', response.body)
        

class MainHandlerSourcePathTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return ThumborServiceApp(get_conf_path('conf1.py'))
    
    def test_validates_passed_url_is_in_valid_source(self):
        self.http_client.fetch(self.get_url('/www.mydomain.com/logo2.jpg'), self.stop)
        response = self.wait()
        self.assertEqual(404, response.code)
        self.assertEqual('Your image source is not allowed!', response.body)

class MainHandlerTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def test_returns_success_status_code(self):
        self.http_client.fetch(self.get_url('/www.globo.com/media/globocom/img/sprite1.png'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
    
    # def test_handler_exists(self):
    #     assert isinstance(self._app, BaseHandler()), 'App does not exist or is not instance of the ThumborServiceApp class'
    # def test_register_new_device(self):
    #     self.http_client.fetch(self.get_url('/'), self.stop)
    #     response = self.wait()
    #     self.assertEqual(self._http_success_code, response.code)
    #     verify(self._registration_handler).handle_registration(self._deviceid, self._registrationid)
    # 
    # def test_update_registration_for_registered_device(self):
    #     self.http_client.fetch(self.get_url(self._successfull_update_registration),
    #         self.stop)
    #     response = self.wait()
    #     self.assertEquals(self._http_success_code, response.code)
    #     verify(self._registration_handler).handle_registration_id_change_for_device(self._deviceid, self._registrationid)

if __name__ == '__main__':
    unittest.main()