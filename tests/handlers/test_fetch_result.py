#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest.mock import Mock

from preggy import expect

from tests.base import TestCase
from thumbor.handlers import FetchResult


class FetchResultTestCase(TestCase):
    def test_can_create_default_fetch_result(self):
        result = FetchResult()
        expect(result.normalized).to_be_false()
        expect(result.buffer).to_be_null()
        expect(result.engine).to_be_null()
        expect(result.successful).to_be_false()
        expect(result.loader_error).to_be_null()

    def test_can_create_fetch_result(self):
        buffer_mock = Mock()
        engine_mock = Mock()
        error_mock = Mock()
        result = FetchResult(
            normalized=True,
            buffer=buffer_mock,
            engine=engine_mock,
            successful=True,
            loader_error=error_mock,
        )
        expect(result.normalized).to_be_true()
        expect(result.buffer).to_equal(buffer_mock)
        expect(result.engine).to_equal(engine_mock)
        expect(result.successful).to_be_true()
        expect(result.loader_error).to_equal(error_mock)
