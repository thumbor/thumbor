#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters import create_instances
from thumbor.filters.fill import Filter
from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer

DATA = [ #size requested, resized/croped image size, result size
	((20, 20), (10, 10), (20, 20)),
    ((20, 0),  (10, 10), (20, 10)),
    ((0,  20), (10, 10), (10, 20))
]

@Vows.batch
class FillFilterVows(Vows.Context):
    def topic(self):
        conf = Config()
        conf.ENGINE = 'thumbor.engines.pil'
        imp = Importer(conf)
        imp.import_modules()
        ctx = Context(None, conf, imp)

        for item in DATA:
            ctx.modules.engine.image = ctx.modules.engine.gen_image(item[1],'#fff')
            req = RequestParameters(fit_in=True,width=item[0][0],height=item[0][1])
            ctx.request = req

            filter_instances = create_instances(ctx, [Filter], "fill(blue)")

            filter_instances[0].run()
            yield (filter_instances[0].engine.image.size,item[2])

    def image_should_be_filled(self, topic):
        expect(topic[0]).to_equal(topic[1])
