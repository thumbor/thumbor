# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest.mock import Mock


from tests.base import TestCase
from thumbor.handlers import FetchResult


class FetchResultTestCase(TestCase):
    def test_can_create_default_fetch_result(self):
        result = FetchResult()
        assert not result.normalized
        assert result.buffer is None
        assert result.engine is None
        assert not result.successful
        assert result.loader_error is None

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
        assert result.normalized
        assert result.buffer == buffer_mock
        assert result.engine == engine_mock
        assert result.successful
        assert result.loader_error == error_mock
