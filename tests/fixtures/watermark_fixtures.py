#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import preggy

POSITIONS = [
    # length (either width or height), position in percent, expected string
    (800, "-20p", "-160"),
    (800, "30p", "240"),
    (800, "230p", "1840"),
    (50, "37p", "19"),
    (55, "53p", "29"),
    (55, "-53p", "-29"),
    (800, "center", "center"),
    (800, "30", "30"),
    (800, "-40", "-40"),
    (800, "repeat", "repeat"),
]


SOURCE_IMAGE_SIZES = [
    (800, 600),
    (600, 600),
    (600, 800),
]

WATERMARK_IMAGE_SIZES = [
    # bigger ones
    (1200, 900),
    (900, 900),
    (900, 1200),
    # one size bigger
    (1200, 500),
    (700, 400),
    (400, 700),
    # equal
    (800, 600),
    (600, 600),
    # smaller
    (500, 300),
    (300, 300),
    (300, 500),
]

RATIOS = [
    # only X
    (300, None),
    (200, None),
    (100, None),
    (50, None),
    (25, None),
    # only Y
    (None, 300),
    (None, 200),
    (None, 100),
    (None, 50),
    (None, 25),
    # X and Y
    (300, 300),
    (200, 200),
    (100, 100),
    (50, 50),
    (25, 25),
    (300, 25),
    (300, 50),
    (300, 100),
    (300, 200),
    (25, 300),
    (50, 300),
    (100, 300),
    (200, 300),
    (25, 50),
    (50, 25),
]


@preggy.assertion
def to_fit_into(topic, boundary, **kwargs):
    assert (
        topic <= boundary
    ), f"Expected topic({topic}) to fit into boundary {boundary} with test: {kwargs}"


@preggy.assertion
def to_be_true_with_additional_info(topic, **kwargs):
    assert topic, f"Expected topic to be true with test: {kwargs}"


@preggy.assertion
def to_be_equal_with_additional_info(topic, expected, **kwargs):
    assert (
        topic == expected
    ), f"Expected topic({topic}) to be ({expected}) with test: {kwargs}"


@preggy.assertion
def to_almost_equal(topic, expected, differ, **kwargs):
    assert abs(1 - topic / expected) <= (differ / 100.0), (
        f"Expected topic({topic}) to be almost equal expected"
        f"({expected}) differing only in {differ}% with test: {kwargs}"
    )
