#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from preggy import expect
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.handlers import BaseHandler

# pylint: disable=broad-except,abstract-method,attribute-defined-outside-init,line-too-long,too-many-public-methods
# pylint: disable=too-many-lines


class TranslateCoordinatesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        coords = self.get_coords()
        crop_coords = BaseHandler.translate_crop_coordinates(
            original_width=coords["original_width"],
            original_height=coords["original_height"],
            width=coords["width"],
            height=coords["height"],
            crop_left=coords["crop_left"],
            crop_top=coords["crop_top"],
            crop_right=coords["crop_right"],
            crop_bottom=coords["crop_bottom"],
        )
        self.translate_crop_coordinates = crop_coords

    def get_coords(self):
        return {
            "original_width": 3000,
            "original_height": 2000,
            "width": 1200,
            "height": 800,
            "crop_left": 100,
            "crop_top": 100,
            "crop_right": 200,
            "crop_bottom": 200,
            "expected_crop": (40, 40, 80, 80),
        }

    @gen_test
    async def test_should_be_a_list_of_coords(self):
        expect(self.translate_crop_coordinates).to_be_instance_of(tuple)

    @gen_test
    async def test_should_translate_from_original_to_resized(self):
        expect(self.translate_crop_coordinates).to_equal(
            self.get_coords()["expected_crop"]
        )
