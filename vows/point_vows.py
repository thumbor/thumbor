#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.point import FocalPoint


@Vows.batch
class FocalPointVows(Vows.Context):

    class DefaultAlignmentPercentages(Vows.Context):
        def topic(self):
            return FocalPoint.ALIGNMENT_PERCENTAGES

        def should_have_left_alignment_of_0(self, topic):
            expect(topic['left']).to_equal(0.0)

        def should_have_center_alignment_of_half(self, topic):
            expect(topic['center']).to_equal(0.5)

        def should_have_right_alignment_of_one(self, topic):
            expect(topic['right']).to_equal(1.0)

        def should_have_top_alignment_of_0(self, topic):
            expect(topic['top']).to_equal(0.0)

        def should_have_middle_alignment_of_half(self, topic):
            expect(topic['middle']).to_equal(0.5)

        def should_have_bottom_alignment_of_one(self, topic):
            expect(topic['bottom']).to_equal(1.0)

    class NewPoint(Vows.Context):

        class DefaultWeight(Vows.Context):
            def topic(self):
                return FocalPoint(10, 20)

            def should_have_x_coord_of_10(self, topic):
                expect(topic.x).to_equal(10)

            def should_have_y_coord_of_20(self, topic):
                expect(topic.y).to_equal(20)

        class Weighted(Vows.Context):
            def topic(self):
                return FocalPoint(x=10, y=20, height=1.0, width=3.0, weight=3.0)

            def should_have_weight_of_three(self, topic):
                expect(topic.weight).to_equal(3.0)

            def should_have_proper_representation(self, topic):
                expect(str(topic)).to_equal('FocalPoint(x: 10, y: 20, width: 3, height: 1, weight: 3, origin: alignment)')

        class FromDict(Vows.Context):
            def topic(self):
                return FocalPoint.from_dict({'x': 10.1, 'y': 20.1, 'z': 5.1})

            def should_have_x_coord_of_10_1(self, topic):
                expect(topic.x).to_equal(10.1)

            def should_have_y_coord_of_20_1(self, topic):
                expect(topic.y).to_equal(20.1)

            def should_have_weight_of_5_1(self, topic):
                expect(topic.weight).to_equal(5.1)

            class ToDict(Vows.Context):
                def topic(self, prev_topic):
                    return prev_topic.to_dict()

                def should_create_the_original_dictionary(self, topic):
                    expect(topic).to_be_like({'x': 10.1, 'y': 20.1, 'z': 5.1, 'origin': 'alignment', 'width': 1.0, 'height': 1.0})

    class SquarePoint(Vows.Context):

        def topic(self):
            return FocalPoint.from_square(x=350, y=50, width=110, height=110)

        def should_have_x_of_450(self, topic):
            expect(topic.x).to_equal(405)

        def should_have_x_of_150(self, topic):
            expect(topic.y).to_equal(105)

        def should_have_weight_of_12100(self, topic):
            expect(topic.weight).to_equal(12100)

    class AlignedPoint(Vows.Context):

        class CenterMiddle(Vows.Context):
            def topic(self):
                return FocalPoint.from_alignment('center', 'middle', 300, 200)

            def should_have_x_of_150(self, topic):
                expect(topic.x).to_equal(150)

            def should_have_y_of_100(self, topic):
                expect(topic.y).to_equal(100)

            def should_have_weight_of_1(self, topic):
                expect(topic.weight).to_equal(1.0)

        class TopLeft(Vows.Context):
            def topic(self):
                return FocalPoint.from_alignment('left', 'top', 300, 200)

            def should_have_x_of_0(self, topic):
                expect(topic.x).to_equal(0)

            def should_have_y_of_0(self, topic):
                expect(topic.y).to_equal(0)

            def should_have_weight_of_1(self, topic):
                expect(topic.weight).to_equal(1.0)

        class BottomRight(Vows.Context):
            def topic(self):
                return FocalPoint.from_alignment('right', 'bottom', 300, 200)

            def should_have_x_of_300(self, topic):
                expect(topic.x).to_equal(300)

            def should_have_y_of_200(self, topic):
                expect(topic.y).to_equal(200)

            def should_have_weight_of_1(self, topic):
                expect(topic.weight).to_equal(1.0)
