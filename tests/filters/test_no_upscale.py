# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2025 globo.com thumbor@googlegroups.com


from tornado.testing import gen_test

from tests.base import FilterTestCase


class NoUpscaleFilterTestCase(FilterTestCase):
    @gen_test
    async def test_no_upscale_filter_marks_request(self):
        def config_context(context):
            context.request.width = 600
            context.request.height = 400

        fltr = self.get_filter(
            "thumbor.filters.no_upscale",
            "no_upscale()",
            config_context=config_context,
        )

        assert not self.context.request.no_upscale

        await fltr.run()

        assert self.context.request.no_upscale
        assert self.context.request.width == 600
        assert self.context.request.height == 400
