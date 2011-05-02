#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from vows.transformer_test_data import TESTITEMS, FIT_IN_CROP_DATA, TestData

from thumbor.transformer import Transformer

class EngineContext(Vows.Context):
    def _get_engine(self, topic):
        context = topic[0].to_context()
        trans = Transformer(context)
        trans.transform()

        return context['engine']

@Vows.assertion
def to_be_resized(topic):
    expect(topic.has_resized_properly()).to_be_true()

@Vows.assertion
def to_be_cropped(topic):
    expect(topic.has_cropped_properly()).to_be_true()

@Vows.batch
class TransformerVows(Vows.Context):

    class InvalidCrop(Vows.Context):
        class InvalidCropPoints(Vows.Context):
            def topic(self):
                data = TestData(
                    source_width=800, source_height=600,
                    target_width=800, target_height=600,
                    halign="right", valign="top",
                    focal_points=[],
                    crop_left=200, crop_top=0, crop_right=100, crop_bottom=100
                )

                ctx = data.to_context()
                trans = Transformer(ctx)
                trans.transform()

                return ctx['engine']

            def should_not_crop(self, topic):
                expect(topic.calls['crop']).to_be_empty()

    class Flip(Vows.Context):
        def topic(self):
            data = TestData(
                        source_width=800, source_height=600,
                        target_width=-800, target_height=-600,
                        halign="right", valign="top",
                        focal_points=[],
                        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
                    )

            ctx = data.to_context()
            trans = Transformer(ctx)
            trans.transform()

            return ctx['engine']

        def should_do_horizontal_flip(self, topic):
            expect(topic.calls['horizontal_flip']).to_equal(1)

        def should_do_vertical_flip(self, topic):
            expect(topic.calls['vertical_flip']).to_equal(1)

    class ResizeCrop(Vows.Context):

        def topic(self):
            for item in TESTITEMS:
                yield item

        def should_resize_properly(self, topic):
            context = topic.to_context()
            trans = Transformer(context)
            trans.transform()

            expect(topic).to_be_resized()

        def should_crop_properly(self, topic):
            context = topic.to_context()
            trans = Transformer(context)
            trans.transform()

            expect(topic).to_be_cropped()

    class FitIn(EngineContext):
        def topic(self):
            for item in FIT_IN_CROP_DATA:
                yield item

        def should_not_have_crop(self, topic):
            engine = self._get_engine(topic)
            expect(engine.calls['crop']).to_be_empty()

        def should_have_resize(self, topic):
            engine = self._get_engine(topic)
            expect(engine.calls['resize']).not_to_be_empty()

        def should_have_only_one_resize_call(self, topic):
            engine = self._get_engine(topic)
            expect(engine.calls['resize']).to_length(1)

        def should_have_proper_width(self, topic):
            engine = self._get_engine(topic)
            expect(engine.calls['resize'][0]['width']).to_equal(topic[1][0])

        def should_have_proper_height(self, topic):
            engine = self._get_engine(topic)
            expect(engine.calls['resize'][0]['height']).to_equal(topic[1][1])
