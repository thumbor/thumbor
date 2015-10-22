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

from thumbor.config import (
    generate_config,
    format_value,
)


class ConfigTestCase(TestCase):
    @mock.patch('derpconf.config.generate_config')
    def test_can_generate_config(self, config_mock):
        generate_config()
        expect(config_mock.called).to_be_true()

    def test_can_format_value(self):
        expect(format_value("qwe")).to_equal("'qwe'")
        expect(format_value(["qwe", "rty"])).to_equal("[\n#    qwe#    rty#]")
        expect(format_value(230)).to_equal(230)
