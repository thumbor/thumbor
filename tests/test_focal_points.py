#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.point import FocalPoint


def test_focal_point():
    point = FocalPoint(x=10.0, y=20.0, weight=3.4)

    assert point.x == 10.0
    assert point.y == 20.0
    assert point.weight == 3.4


def test_default_weight_is_one():
    point = FocalPoint(x=10.0, y=20.0)

    assert point.weight == 1.0


def test_from_square():
    point = FocalPoint.from_square(x=10.0, y=20.0, width=100, height=200)
    assert point.x == 55.0
    assert point.y == 110.0
    assert point.weight == 20000.0


def test_focal_points_alignments():
    for point in [
        ('left', 'top', 100, 200, 0.0, 0.0),
        ('left', 'middle', 100, 200, 0.0, 100.0),
        ('left', 'bottom', 100, 200, 0.0, 200.0),
        ('center', 'top', 100, 200, 50.0, 0.0),
        ('center', 'middle', 100, 200, 50.0, 100.0),
        ('center', 'bottom', 100, 200, 50.0, 200.0),
        ('right', 'top', 100, 200, 100.0, 0.0),
        ('right', 'middle', 100, 200, 100.0, 100.0),
        ('right', 'bottom', 100, 200, 100.0, 200.0)
    ]:
        yield assert_point_from_alignment, point


def assert_point_from_alignment(point):
    comp_point = FocalPoint.from_alignment(point[0], point[1], width=point[2], height=point[3])

    assert comp_point.x == point[4], "Expected x => %.2f Got x => %.2f" % (point[4], comp_point.x)
    assert comp_point.y == point[5], "Expected y => %.2f Got y => %.2f" % (point[5], comp_point.y)
    assert comp_point.weight == 1.0
