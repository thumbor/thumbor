#!/usr/bin/python
# -*- coding: utf-8 -*-

from thumbor.transformer import Transformer
from thumbor.point import FocalPoint as fp
from transform_helper import TestData


TESTITEMS = [
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=150, crop_right=800, crop_bottom=450
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=150, crop_top=0, crop_right=450, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=0, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=140,
        target_width=180, target_height=100,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=14, crop_right=200, crop_bottom=125
    ),
    
    # tests with focal points
    TestData(
        source_width=200, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=75.0, crop_top=0, crop_right=175.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=225.0, crop_top=0, crop_right=325.0, crop_bottom=200
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(50, 100, 1), fp(50, 300, 1), fp(150, 100, 1), fp(150, 300, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
]

def test_transformer():
    for data in TESTITEMS:
        yield assert_proper_operations, data

def assert_proper_operations(data):
    trans = Transformer(data.to_context(), data.source_width, data.source_height)
    trans.transform()

    assert data.has_cropped_properly(), data.crop_error_message
    assert data.has_resized_properly(), data.resize_error_message
