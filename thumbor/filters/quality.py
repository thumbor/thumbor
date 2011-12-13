#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter

class Filter(BaseFilter):
    regex = r'(?:quality\((?P<value>[\d]+)\))'

    def run_filter(self):
        self.context['quality'] = int(self.params['value'])
