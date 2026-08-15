# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import pytest
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.compatibility import compatibility_get


def get_result(first, second, callback):
    callback(first, second, True)


class SimpleCompatibilityTestCase(TestCase):
    @gen_test
    async def test_can_get_result(self):
        first, second, response = await compatibility_get(
            1, second=2, func=get_result
        )
        assert first == 1
        assert second == 2
        assert response is True

    @gen_test
    async def test_fails_without_func(self):
        msg = (
            "'func' argument can't be None when calling thumbor's "
            "compatibility layer."
        )
        with pytest.raises(RuntimeError, match=msg):
            await compatibility_get(1, second=2)
