#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from thumbor.context import Context, RequestParameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.filters.rotate import Filter
import thumbor.filters

from tests.base import FilterTestCase


class RotateFilterTestCase(FilterTestCase):
    def test_rotate_filter(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.rotate', 'rotate(180)')
        expected = self.get_fixture('rotate.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.97)

    def test_rotate_filter_with_invalid_value(self):
        image = self.get_filtered('source.jpg', 'thumbor.filters.rotate', 'rotate(181)')
        expected = self.get_fixture('source.jpg')

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_equal(1)


class FakeRotateEngine(object):
    def __init__(self):
        self.rotate_val = None

    def rotate(self, rotate_val):
        self.rotate_val = rotate_val

    def is_multiple(self):
        return False


class FakeRotateEngineRotateFilterTestCase(FilterTestCase):
    def setUp(self, *args, **kwargs):
        super(FakeRotateEngineRotateFilterTestCase, self).setUp(*args, **kwargs)
        conf = Config()
        imp = Importer(conf)
        imp.filters = [Filter]
        self.context = Context(None, conf, imp)
        self.context.request = RequestParameters()

    def test_disallows_invalid_context_should_be_none(self):
        runner = self.context.filters_factory.create_instances(self.context, "rotate(91)")
        filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        filter_instances[0].engine = FakeRotateEngine()
        filter_instances[0].run()
        expect(filter_instances[0].engine.rotate_val).to_be_null()

    def test_should_equal_90(self):
        runner = self.context.filters_factory.create_instances(self.context, "rotate(90)")
        filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        filter_instances[0].engine = FakeRotateEngine()
        filter_instances[0].run()
        expect(filter_instances[0].engine.rotate_val).to_equal(90)

    def test_normalized_rotate_should_equal_180(self):
        runner = self.context.filters_factory.create_instances(self.context, "rotate(540)")
        filter_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        filter_instances[0].engine = FakeRotateEngine()
        filter_instances[0].run()
        expect(filter_instances[0].engine.rotate_val).to_equal(180)
