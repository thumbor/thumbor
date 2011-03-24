#!/usr/bin/python
# -*- coding: utf-8 -*-

from thumbor.transformer import Transformer
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
    )

]

def test_transformer():
    for data in TESTITEMS:
        yield assert_proper_operations, data

def assert_proper_operations(data):
    trans = Transformer(data.to_context(), data.source_width, data.source_height)
    trans.transform()

    assert data.has_cropped_properly(), data.crop_error_message
    assert data.has_resized_properly(), data.resize_error_message
