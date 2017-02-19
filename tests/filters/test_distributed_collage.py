#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import FilterTestCase


class DistributedCollageFilterTestCase(FilterTestCase):
    urls = (
        '800px-Guido-portrait-2014.jpg',
        '800px-Katherine_Maher.jpg',
        'Giunchedi%2C_Filippo_January_2015_01.jpg',
        '800px-Christophe_Henner_-_June_2016.jpg',
        '800px-Coffee_berries_1.jpg',
        '800px-A_small_cup_of_coffee.JPG',
        '513px-Coffee_beans_-_ziarna_kawy.jpg',
    )

    def test_fallback_when_have_not_enough_images(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,)')
        expected = self.get_fixture('distributed_collage_fallback.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)

    def test_with_one_image(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[:1]))
        expected = self.get_fixture('distributed_collage_1i.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_with_two_images(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[:2]))
        expected = self.get_fixture('distributed_collage_2i.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_with_three_images(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[:3]))
        expected = self.get_fixture('distributed_collage_3i.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_with_four_images(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[:4]))
        expected = self.get_fixture('distributed_collage_4i.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.89)

    def test_with_two_images_centered_when_no_feature_detected(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[4:6]))
        expected = self.get_fixture('distributed_collage_2i_centered.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_with_two_images_of_different_heights(self):
        def config_context(context):
            context.request.width = 200
            context.request.height = 200
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s)' % '|'.join(self.urls[5:]),
            config_context)
        expected = self.get_fixture('distributed_collage_2i_diff_heights.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)

    def test_show_fallback_when_exceed_the_maximun_of_four_images(self):
        image = self.get_filtered(
            'distributed_collage_fallback.png',
            'thumbor.filters.distributed_collage',
            'distributed_collage(horizontal,smart,%s|%s)' % (
                '|'.join(self.urls[:4]),
                self.urls[1]
            ))
        expected = self.get_fixture('distributed_collage_fallback.png')
        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.98)
