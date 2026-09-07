# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import pytest

from thumbor.ext.filters import _sharpen


@pytest.mark.parametrize("size", [1, 2, 15, 16, 31, 32])
def test_sharpen_accepts_small_dimensions(size):
    buffer = bytes([128, 128, 128] * size * size)

    result = _sharpen.apply("RGB", size, size, 1.0, 1.0, False, buffer)

    assert isinstance(result, bytes)
    assert len(result) == len(buffer)


def test_sharpen_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        _sharpen.apply("RGB", 0, 1, 1.0, 1.0, False, bytes([128, 128, 128]))


def test_sharpen_rejects_short_buffer():
    with pytest.raises(ValueError):
        _sharpen.apply("RGB", 2, 2, 1.0, 1.0, False, bytes([128, 128, 128]))
