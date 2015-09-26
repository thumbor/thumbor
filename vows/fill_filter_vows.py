#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters.fill import Filter
from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer
import thumbor.filters

DATA = [
    # size requested, resized/cropped image size, result size, image color, detected color
    ((20, 20), (10, 10), (20, 20), '#fff', "ffffff"),
    ((20, 0), (10, 10), (20, 10), '#333', "333333"),
    ((0, 20), (10, 10), (10, 20), '#123103', "123103")
]


def get_context():
    conf = Config()
    conf.ENGINE = 'thumbor.engines.pil'
    imp = Importer(conf)
    imp.import_modules()
    imp.filters = [Filter]
    return Context(None, conf, imp)


@Vows.batch
class FillFilterVows(Vows.Context):

    class checkImageSizes():

        def topic(self):
            ctx = get_context()
            for item in DATA:
                ctx.modules.engine.image = ctx.modules.engine.gen_image(item[1], '#fff')
                req = RequestParameters(fit_in=True, width=item[0][0], height=item[0][1])
                ctx.request = req

                runner = ctx.filters_factory.create_instances(ctx, "fill(blue)")
                filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
                filter_instances[0].run()
                yield (filter_instances[0].engine.image.size, item[2])

        def image_should_be_filled(self, topic):
            expect(topic[0]).to_equal(topic[1])

    class checkFilterWithFillTransparent():

        def topic(self):
            ctx = get_context()
            ctx.modules.engine.image = ctx.modules.engine.gen_image((10, 10), 'rgba(0,0,0,0)')
            req = RequestParameters(width=10, height=10)
            ctx.request = req

            runner = ctx.filters_factory.create_instances(ctx, "fill(ff0000, true)")
            filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
            filter_instances[0].run()
            return ctx.modules.engine

        def image_should_be_filled(self, topic):
            expect(topic).not_to_be_an_error()
            data = topic.get_image_data()
            expect(data).to_equal('\xff\x00\x00\xff' * 100)

    class checkFilterWithoutFillTransparent():

        def topic(self):
            ctx = get_context()
            ctx.modules.engine.image = ctx.modules.engine.gen_image((10, 10), 'rgba(0,0,0,0)')
            req = RequestParameters(width=10, height=10)
            ctx.request = req

            runner = ctx.filters_factory.create_instances(ctx, "fill(ff0000, false)")
            filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
            filter_instances[0].run()
            return ctx.modules.engine

        def image_should_be_filled(self, topic):
            expect(topic).not_to_be_an_error()
            data = topic.get_image_data()
            expect(data).to_equal('\x00\x00\x00\x00' * 100)

    class checkAutoDetectedColor():

        def topic(self):
            ctx = get_context()
            for item in DATA:
                (size_requested, size_cropped, size_results, image_color, detected_color) = item

                ctx.modules.engine.image = ctx.modules.engine.gen_image(size_cropped, image_color)
                req = RequestParameters(fit_in=True, width=size_requested[0], height=size_requested[1])
                ctx.request = req

                runner = ctx.filters_factory.create_instances(ctx, "fill(auto)")
                filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

                yield (filter_instances[0].get_median_color(), detected_color)

        def the_median_color_should_be_detected(self, topic):
            expect(topic).not_to_be_an_error()
            expect(topic[0]).to_equal(topic[1])
