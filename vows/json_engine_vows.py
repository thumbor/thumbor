#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from json import loads

from pyvows import Vows, expect
ctx = Vows.Context

from thumbor.engines.json_engine import JSONEngine

class MockImage:
    def __init__(self, size, data=None):
        self.size = size
        self.data = data

class MockEngine:
    def __init__(self, size):
        self.context = None
        self.image = MockImage(size)

    def get_image_mode(self):
        return 'RGB'

    def get_image_data(self):
        return self.image.data

    def set_image_data(self, data):
        self.image.data = data

    def resize(self, width, height):
        self.image.size = (width, height)

    @property
    def size(self):
        return self.image.size

IMAGE_PATH = '/some/image/path.jpg'
IMAGE_SIZE = (300, 200)

@Vows.batch
class JsonEngineVows(ctx):

    class CreateInstanceVows(ctx):
        def topic(self):
            engine = MockEngine(size=IMAGE_SIZE)
            json = JSONEngine(engine=engine, path=IMAGE_PATH)

            return json

        def should_not_be_null_or_error(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        def should_have_proper_engine(self, topic):
            expect(topic.engine).to_be_instance_of(MockEngine)

        def should_have_proper_dimensions(self, topic):
            expect(topic.width).to_equal(300)
            expect(topic.height).to_equal(200)

        def should_have_proper_path(self, topic):
            expect(topic.path).to_equal(IMAGE_PATH)

        def should_have_null_callback_name(self, topic):
            expect(topic.callback_name).to_be_null()

        def should_have_empty_operations(self, topic):
            expect(topic.operations).to_be_empty()

        def should_have_empty_focal_points(self, topic):
            expect(topic.focal_points).to_be_empty()

        def should_have_proper_image(self, topic):
            expect(topic.image).to_be_instance_of(MockImage)

        def should_return_size(self, topic):
            expect(topic.size).to_equal((300, 200))

        class GetImageMode(ctx):
            def topic(self, engine):
                return engine.get_image_mode()

            def should_return_proper_image_mode(self, topic):
                expect(topic).to_equal('RGB')

        class GetImageData(ctx):
            def topic(self, engine):
                engine.set_image_data('SOME DATA')
                return engine.get_image_data()

            def should_return_proper_image_data(self, topic):
                expect(topic).to_equal('SOME DATA')

        class Read(ctx):
            def topic(self, engine):
                return loads(engine.read('jpg', 100))

            def should_be_proper_json(self, topic):
                expected = {
                    "thumbor": {
                        "operations": [],
                        "source": {
                            "url": "/some/image/path.jpg",
                            "width": 300, 
                            "height": 200
                        },
                        "target": {
                            "width": 300, 
                            "height": 200
                        }
                    }
                }
                expect(topic).to_be_like(expected)

    class ResizeVows(ctx):
        def topic(self):
            engine = MockEngine(size=IMAGE_SIZE)
            json = JSONEngine(engine=engine, path=IMAGE_PATH)

            json.resize(200, 300)

            return loads(json.read('jpg', 100))

        def should_be_proper_json(self, topic):
            expected = {
                "thumbor": {
                    "operations": [
                        {u'width': 200, u'type': u'resize', u'height': 300}
                    ],
                    "source": {
                        "url": "/some/image/path.jpg",
                        "width": 300, 
                        "height": 200
                    },
                    "target": {
                        "width": 200, 
                        "height": 300
                    }
                }
            }
            expect(topic).to_be_like(expected)


