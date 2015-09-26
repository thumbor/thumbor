#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

from thumbor.filters.drop_shadow import Filter


def test_drop_shadow_filter_regex():
    reg = Filter.regex

    url = '''shadow(10, 10, "#ffffff", '#000000')/'''

    match = re.match(reg, url)

    assert match

    keys = match.groupdict()

    assert keys
    assert 'drop_shadow' in keys
    assert keys['drop_shadow'] == 'shadow(10, 10, "#ffffff", \'#000000\')', keys['drop_shadow']
