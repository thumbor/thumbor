#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.handlers import BaseHandler

DATA = [
    dict(
        original_width=3000,
        original_height=2000,
        width=1200,
        height=800,
        crop_left=100,
        crop_top=100,
        crop_right=200,
        crop_bottom=200,
        expected_crop=(40, 40, 80, 80)
    )
]


@Vows.batch
class TranslateCoordinatesContext(Vows.Context):

    def topic(self):
        for coords in DATA:
            yield coords

    class CoordContext(Vows.Context):
        def topic(self, coords):
            return (BaseHandler.translate_crop_coordinates(
                original_width=coords['original_width'],
                original_height=coords['original_height'],
                width=coords['width'],
                height=coords['height'],
                crop_left=coords['crop_left'],
                crop_top=coords['crop_top'],
                crop_right=coords['crop_right'],
                crop_bottom=coords['crop_bottom']
            ), coords)

        def should_be_a_list_of_coords(self, topic):
            expect(topic[0]).to_be_instance_of(tuple)

        def should_translate_from_original_to_resized(self, topic):
            expect(topic[0]).to_equal(topic[1]['expected_crop'])
