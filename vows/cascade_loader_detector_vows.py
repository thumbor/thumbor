#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os import path

from pyvows import Vows, expect
ctx = Vows.Context

from mock import Mock
from thumbor.detectors.local_detector import CascadeLoaderDetector
from thumbor.point import FocalPoint


cascade_file_path = path.join(
    __file__, '..', '..', 'thumbor',
    'detectors', 'face_detector', 'haarcascade_frontalface_alt.xml')
CASCADE_FILE_PATH = path.abspath(cascade_file_path)


@Vows.batch
class CascadeLoaderDetectorVows(ctx):

    class CreateInstanceVows(ctx):
        def topic(self):
            return CascadeLoaderDetector("context", 1, "detectors")

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        class LoadCascadefile(ctx):

            def topic(self, detector):
                detector.load_cascade_file(None, CASCADE_FILE_PATH)
                return detector

            def should_set_the_cascade_attribute_in_the_class(self, topic):
                # ugly check because there is no becautifull way to see
                # if this object is an instance of some class or if it has some
                # kind of attribute
                expect(repr(topic.__class__.cascade)).to_include('<CascadeClassifier')

        class GetMinSizeFor(ctx):

            def topic(self, detector):
                return detector.get_min_size_for((400, 700))

            def should_return_the_expected_min_size(self, topic):
                expect(topic).to_equal((26, 26))

        class Detect(ctx):

            def topic(self, detector):
                detector.context = Mock()
                detector.get_features = Mock(return_value=[((1, 2, 3, 4), 10), ((5, 6, 7, 8), 11)])
                detector.detect(lambda: None)
                return detector

            def should_append_2_focal_points_to_context_request(self, topic):
                expect(topic.context.request.focal_points.append.call_count).to_equal(2)

            def should_append_the_returned_focal_points_to_context_request(self, topic):
                focal_point1_repr = FocalPoint.from_square(1, 2, 3, 4).to_dict()
                focal_point2_repr = FocalPoint.from_square(5, 6, 7, 8).to_dict()

                calls = topic.context.request.focal_points.append.call_args_list

                first_call_arg_repr = calls[0][0][0].to_dict()
                secon_call_arg_repr = calls[1][0][0].to_dict()

                expect(first_call_arg_repr).to_equal(focal_point1_repr)
                expect(secon_call_arg_repr).to_equal(focal_point2_repr)
