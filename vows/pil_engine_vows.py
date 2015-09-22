#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.config import Config
from thumbor.importer import Importer

from pyvows import Vows, expect
ctx = Vows.Context

import thumbor.engines.pil as PIL

from os.path import join, abspath, dirname
FIXTURES_FOLDER = join(abspath(dirname(__file__)), 'fixtures')

class MockImage:
    def __init__(self, mode, width, height):
        self.mode = mode
        self.width = width
        self.height = height
        self.calls = []
    def convert(self, mode):
        self.calls.append('convert')
        self.mode = mode
        return self
    def resize(self, size, filter):
        self.calls.append('resize')
        self.width = size[0]
        self.height = size[1]
        return self

def engine_with_buffer():
    config = Config()
    server = ServerParameters(
        8889, 'localhost', 'thumbor.conf', None, 'info', None
    )

    context = Context(server, config, Importer(config))
    config.QUALITY = 42

    with open("%s/image.jpg" % FIXTURES_FOLDER, "rb") as f:
        buffer = f.read()

    engine = PIL.Engine(context=context)
    engine.load(buffer, '.jpg')
    return engine

@Vows.batch
class PilEngineVows(ctx):

    class WritingJpegImageWithoutResize(ctx):
        def topic(self):
            engine = engine_with_buffer()
            engine.read('.jpg', None);
            # unchanged, so this is the original image object
            return engine.image

        def should_keep_quality(self, image):
            expect(image.encoderinfo.get('quality')).to_equal('keep')


    class WritingJpegImageWithResize(ctx):
        def topic(self):
            engine = engine_with_buffer()
            engine.resize(200,200)
            engine.read('.jpg', None);
            # resized, so this was replaced by a new image object
            return engine.image

        def should_keep_quality(self, image):
            expect(image.encoderinfo.get('quality')).to_equal('keep')



    class ResizedPaletteImage(ctx):
        def topic(self):
            engine = PIL.Engine(None)
            engine.image = MockImage('P', 640, 480)
            engine.resize(320, 240)
            return engine.image
        def should_convert_p_to_rgba(self, image):
            expect(image.mode).to_equal('RGBA')
            expect((image.width, image.height)).to_equal((320, 240))
            expect(image.calls.index('convert') < image.calls.index('resize')).to_be_true()

    class ResizedNonPaletteImage(ctx):
        def topic(self):
            engine = PIL.Engine(None)
            engine.image = MockImage('other', 640, 480)
            engine.resize(160, 120)
            return engine.image
        def should_not_convert_non_palette_images(self, image):
            expect(image.mode).to_equal('other') # unchanged
            expect((image.width, image.height)).to_equal((160, 120))
            expect(image.calls).Not.to_include(['convert'])

    class ShouldRaiseIfFiltersNotAvailable(ctx):

        @Vows.capture_error
        def topic(self):
            FILTERS_AVAILABLE_BAK = PIL.FILTERS_AVAILABLE
            PIL.FILTERS_AVAILABLE = False
            engine = PIL.Engine(None)
            try:
                return engine.paste(None, None, True)
            finally:
                PIL.FILTERS_AVAILABLE = FILTERS_AVAILABLE_BAK

        def should_be_an_error(self, topic):
            expect(topic).to_be_an_error()
            expect(topic).to_be_an_error_like(RuntimeError)
            expected = 'You need filters enabled to use paste with merge. Please reinstall thumbor with proper ' + \
                'compilation of its filters.'
            expect(topic).to_have_an_error_message_of(expected)
