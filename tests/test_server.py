#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase
import mock

from preggy import expect

from thumbor.config import Config
from thumbor.server import (
    get_as_integer,
    get_config,
    configure_log,
)


class ServerTestCase(TestCase):
    def test_can_get_value_as_integer(self):
        expect(get_as_integer("1")).to_equal(1)
        expect(get_as_integer("a")).to_be_null()
        expect(get_as_integer("")).to_be_null()
        expect(get_as_integer(None)).to_be_null()

    def test_can_get_config_from_path(self):
        config = get_config('./tests/fixtures/thumbor_config_server_test.conf')

        expect(config).not_to_be_null()
        expect(config.ALLOWED_SOURCES).to_be_like(['mydomain.com'])

    @mock.patch('logging.basicConfig')
    def test_can_configure_log_from_config(self, basic_config_mock):
        conf = Config()
        configure_log(conf, 'DEBUG')

        params = dict(
            datefmt='%Y-%m-%d %H:%M:%S',
            level=10,
            format='%(asctime)s %(name)s:%(levelname)s %(message)s'
        )

        basic_config_mock.assert_called_with(**params)

    @mock.patch('logging.config.dictConfig')
    def test_can_configure_log_from_dict_config(self, dict_config_mock):
        conf = Config(
            THUMBOR_LOG_CONFIG={
                "level": "INFO"
            }
        )
        configure_log(conf, 'DEBUG')

        params = dict(
            level="INFO",
        )

        dict_config_mock.assert_called_with(params)
