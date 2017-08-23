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
    (800, '-20p', '-160'),
    (800, '30p', '240'),
    (800, '230p', '1840'),
    (50,  '37p', '19'),
    (55,  '53p', '29'),
    (55,  '-53p', '-29'),
    (800, 'center', 'center'),
    (800, '30', '30'),
    (800, '-40', '-40'),
    (800, 'repeat', 'repeat'),
]


@preggy.assertion
def to_be_equal_with_additional_info(topic, expected, **kwargs):
    assert topic == expected, \
        "Expected topic({topic}) to be ({expected}) with test: {test}".format(
            topic=topic, expected=expected, test=kwargs
        )
