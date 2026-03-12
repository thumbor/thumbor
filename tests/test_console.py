# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase

from thumbor.console import get_server_parameters


class ConsoleTestCase(TestCase):
    def test_can_get_default_server_parameters(self):
        params = get_server_parameters()
        assert params.port == 8888
        assert params.ip == "0.0.0.0"
        assert params.config_path is None
        assert params.keyfile is None
        assert params.log_level == "warning"
        assert params.app_class == "thumbor.app.ThumborServiceApp"
        assert params.fd is None
        assert params.processes == 1

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
        assert params.port == 9999
        assert params.ip == "127.0.0.1"
        assert params.config_path == "/tmp/conf.conf"  # NOSONAR
        assert params.keyfile == "./tests/fixtures/thumbor.key"
        assert params.log_level == "debug"
        assert params.app_class == "custom.app"
        assert params.fd == "/tmp/fd"  # NOSONAR
        assert params.processes == 5
