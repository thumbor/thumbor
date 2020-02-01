# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.filters import PHASE_PRE_LOAD, BaseFilter, filter_method


class Filter(BaseFilter):
    phase = PHASE_PRE_LOAD

    @filter_method()
    async def stretch(self):
        self.context.request.stretch = True
