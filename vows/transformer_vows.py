#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from vows.transformer_test_data import TESTITEMS, FIT_IN_CROP_DATA, TestData, MockSyncDetector, MockErrorSyncDetector

from thumbor.transformer import Transformer


class EngineContext(Vows.Context):
    def _prepare_engine(self, topic, callback):
        context = topic[0].to_context()
        self.engine = context.modules.engine
        self.test_data = topic

        trans = Transformer(context)
        trans.transform(callback)


@Vows.assertion
def to_be_resized(topic):
    expect(topic.has_resized_properly()).to_be_true()


@Vows.assertion
def to_be_cropped(topic):
    expect(topic.has_cropped_properly()).to_be_true()


@Vows.batch
class TransformerVows(Vows.Context):
    class InvalidCrop(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            data = TestData(
                source_width=800, source_height=600,
                target_width=800, target_height=600,
                halign="right", valign="top",
                focal_points=[],
                crop_left=200, crop_top=0, crop_right=100, crop_bottom=100
            )

            ctx = data.to_context()
            self.engine = ctx.modules.engine

            trans = Transformer(ctx)
            trans.transform(callback)

        def should_not_crop(self, topic):
            expect(self.engine.calls['crop']).to_be_empty()

    class MetaWithOrientation(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            data = TestData(
                source_width=800, source_height=600,
                target_width=100, target_height=100,
                halign="right", valign="top",
                focal_points=[],
                crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
                meta=True
            )

            ctx = data.to_context()
            ctx.config.RESPECT_ORIENTATION = True
            self.engine = ctx.modules.engine

            trans = Transformer(ctx)
            trans.transform(callback)

        def should_work_well(self, topic):
            expect(topic).to_be_true()

    class Flip(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            data = TestData(
                source_width=800, source_height=600,
                target_width=-800, target_height=-600,
                halign="right", valign="top",
                focal_points=[],
                crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
            )

            ctx = data.to_context()
            self.engine = ctx.modules.engine

            trans = Transformer(ctx)
            trans.transform(callback)

        def should_do_horizontal_flip(self, topic):
            expect(self.engine.calls['horizontal_flip']).to_equal(1)

        def should_do_vertical_flip(self, topic):
            expect(self.engine.calls['vertical_flip']).to_equal(1)

    class ExtractCover(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            data = TestData(
                source_width=800, source_height=600,
                target_width=-800, target_height=-600,
                halign="right", valign="top",
                focal_points=[],
                crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
            )

            ctx = data.to_context()
            ctx.request.filters = 'cover()'
            ctx.request.image = 'some.gif'
            ctx.request.extension = 'GIF'
            ctx.request.engine.extension = '.gif'
            ctx.config.USE_GIFSICLE_ENGINE = True

            self.engine = ctx.modules.engine

            trans = Transformer(ctx)
            trans.transform(callback)

        def should_do_extract_cover(self, topic):
            expect(self.engine.calls['cover']).to_equal(1)


    class ResizeCrop(Vows.Context):
        def topic(self):
            for item in TESTITEMS:
                yield item

        class AsyncResizeCrop(Vows.Context):
            @Vows.async_topic
            def topic(self, callback, topic):
                self.test_data = topic
                context = topic.to_context()
                trans = Transformer(context)
                trans.transform(callback)

            def should_resize_properly(self, topic):
                expect(self.test_data).to_be_resized()

            def should_crop_properly(self, topic):
                expect(self.test_data).to_be_cropped()

    class ResizeCropWithDetectors(Vows.Context):
        def topic(self):
            for item in TESTITEMS:
                yield item

        class AsyncResizeCrop(Vows.Context):
            @Vows.async_topic
            def topic(self, callback, topic):
                self.test_data = topic
                context = topic.to_context(detectors=[MockSyncDetector])
                trans = Transformer(context)
                trans.transform(callback)

            def should_resize_properly(self, topic):
                expect(self.test_data).to_be_resized()

            def should_crop_properly(self, topic):
                expect(self.test_data).to_be_cropped()

    class ResizeCropWithDetectorErrorsIgnored(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            self.test_data = TestData(
                source_width=800, source_height=600,
                target_width=400, target_height=150,
                halign="center", valign="middle",
                focal_points=[],
                crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
            )
            context = self.test_data.to_context(detectors=[MockErrorSyncDetector], ignore_detector_error=True)
            trans = Transformer(context)
            trans.transform(callback)

        def should_resize_properly(self, topic):
            expect(self.test_data).to_be_resized()

        def should_crop_properly(self, topic):
            expect(self.test_data).to_be_cropped()

    class ResizeCropWithoutDetectorErrorsIgnored(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            self.test_data = TestData(
                source_width=800, source_height=600,
                target_width=400, target_height=150,
                halign="center", valign="middle",
                focal_points=[],
                crop_left=0, crop_top=75, crop_right=800, crop_bottom=375
            )
            context = self.test_data.to_context(detectors=[MockErrorSyncDetector], ignore_detector_error=False)
            trans = Transformer(context)
            trans.transform(callback)

        def should_resize_properly(self, topic):
            expect(self.test_data.engine.calls['resize']).to_length(0)

    class FitIn(Vows.Context):
        def topic(self, callback):
            for item in FIT_IN_CROP_DATA:
                yield item

        class AsyncFitIn(EngineContext):
            @Vows.async_topic
            def topic(self, callback, topic):
                self._prepare_engine(topic, callback)

            def should_not_have_crop(self, topic):
                expect(self.engine.calls['crop']).to_be_empty()

            def should_have_resize(self, topic):
                if not self.test_data[1][2]:
                    expect(self.engine.calls['resize']).to_be_empty()
                    return

                expect(self.engine.calls['resize']).not_to_be_empty()

            def should_have_proper_resize_calls(self, topic):
                length = self.test_data[1][2]
                expect(self.engine.calls['resize']).to_length(length)

            def should_have_proper_width(self, topic):
                if not self.test_data[1][2]:
                    return
                expect(self.engine.calls['resize'][0]['width']).to_equal(self.test_data[1][0])

            def should_have_proper_height(self, topic):
                if not self.test_data[1][2]:
                    return
                expect(self.engine.calls['resize'][0]['height']).to_equal(self.test_data[1][1])
