#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.result_storages.no_storage import Storage as NoStorage


@Vows.batch
class ResultStoragesNoStorageVows(Vows.Context):
    class GetNoneResult(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            config = Config()
            context = Context(config=config)
            context.request = RequestParameters(url='image.jpg')
            fs = NoStorage(context)
            fs.get(callback=callback)

        def check_has_no_image(self, topic):
            result = topic.args[0]
            expect(result).to_be_none

    class PutNoStorage(Vows.Context):
        def topic(self):
            config = Config()
            context = Context(config=config)
            context.request = RequestParameters(url='image.jpg')
            fs = NoStorage(context)
            return fs.put(100)

        def check_can_put_image(self, topic):
            expect(topic).to_equal('')
