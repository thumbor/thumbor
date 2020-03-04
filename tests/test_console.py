#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase

from preggy import expect

from thumbor.console import get_server_parameters


class ConsoleTestCase(TestCase):
    def test_can_get_default_server_parameters(self):
        params = get_server_parameters()
        expect(params.port).to_equal(8888)
        expect(params.ip).to_equal("0.0.0.0")
        expect(params.config_path).to_be_null()
        expect(params.keyfile).to_be_null()
        expect(params.log_level).to_equal("warning")
        expect(params.app_class).to_equal("thumbor.app.ThumborServiceApp")
        expect(params.fd).to_be_null()
        expect(params.processes).to_equal(1)

    def test_can_get_custom_server_parameters(self):
        params = get_server_parameters(
            [
                "--port=9999",
                "--ip=127.0.0.1",
                "--conf=/tmp/conf.conf",
                "--keyfile=./tests/fixtures/thumbor.key",
                "--log-level=debug",
                "--app=custom.app",
                "--fd=/tmp/fd",
                "--processes=5",
            ]
        )
        expect(params.port).to_equal(9999)
        expect(params.ip).to_equal("127.0.0.1")
        expect(params.config_path).to_equal("/tmp/conf.conf")
        expect(params.keyfile).to_equal("./tests/fixtures/thumbor.key")
        expect(params.log_level).to_equal("debug")
        expect(params.app_class).to_equal("custom.app")
        expect(params.fd).to_equal("/tmp/fd")
        expect(params.processes).to_equal(5)
