# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

from thumbor.ext.filters import _curve

IDENTITY = ((0, 0), (255, 255))


def apply_curve(curve, pixel):
    return _curve.apply("RGB", bytes(pixel), IDENTITY, curve, curve, curve)


def test_curve_keeps_first_point_value_below_its_x():
    curve = ((40, 46), (64, 55), (255, 255))

    assert apply_curve(curve, [10, 39, 40]) == bytes([46, 46, 46])


def test_curve_keeps_last_point_value_above_its_x():
    curve = ((0, 0), (200, 100))

    assert apply_curve(curve, [200, 250, 255]) == bytes([100, 100, 100])


def test_curve_rounds_linear_segments():
    assert apply_curve(((0, 0), (3, 1)), [1, 2, 3]) == bytes([0, 1, 1])


def test_curve_rounds_spline_segments():
    curve = ((0, 0), (128, 200), (255, 255))

    assert apply_curve(curve, [7, 64, 191]) == bytes([13, 114, 241])
