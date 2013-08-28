#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters.fill import Filter
from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer

DATA = [
    # size requested, resized/cropped image size, result size, image color, detected color
    ((20, 20), (10, 10), (20, 20), '#fff', "ffffff"),
    ((20, 0), (10, 10), (20, 10), '#333', "333333"),
    ((0, 20), (10, 10), (10, 20), '#123103', "123103")
]


@Vows.batch
class FillFilterVows(Vows.Context):

    class withContext():

        def topic(self):
            conf = Config()
            conf.ENGINE = 'thumbor.engines.pil'
            imp = Importer(conf)
            imp.import_modules()
            imp.filters = [Filter]
            return Context(None, conf, imp)

        class checkImageSizes():

            def topic(self, ctx):
                for item in DATA:
                    ctx.modules.engine.image = ctx.modules.engine.gen_image(item[1], '#fff')
                    req = RequestParameters(fit_in=True, width=item[0][0], height=item[0][1])
                    ctx.request = req

                    filter_instances = ctx.filters_factory.create_instances(ctx, "fill(blue)")
                    filter_instances[0].run()
                    yield (filter_instances[0].engine.image.size, item[2])

            def image_should_be_filled(self, topic):
                expect(topic[0]).to_equal(topic[1])

        class checkAutoDetectedColor():

            def topic(self, ctx):
                for item in DATA:
                    (size_requested, size_cropped, size_results, image_color, detected_color) = item

                    ctx.modules.engine.image = ctx.modules.engine.gen_image(size_cropped, image_color)
                    req = RequestParameters(fit_in=True, width=size_requested[0], height=size_requested[1])
                    ctx.request = req

                    filter_instances = ctx.filters_factory.create_instances(ctx, "fill(auto)")

                    yield (filter_instances[0].get_median_color(), detected_color)

            def the_median_color_should_be_detected(self, topic):
                expect(topic).not_to_be_an_error()
                expect(topic[0]).to_equal(topic[1])
