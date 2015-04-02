# -*- coding: utf-8 -*-

from io import BytesIO
from os.path import join, abspath, dirname
from PIL import Image
from pyvows import Vows, expect
from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.engines.gif import Engine as GifEngine
from thumbor.utils import which


FIXTURES_FOLDER = join(abspath(dirname(__file__)), 'fixtures')


class MockInvalidResultEngine(GifEngine):
    '''Mock some GifEngine methods to generate invalid results.'''

    def __init__(self, **kwargs):
        super(MockInvalidResultEngine, self).__init__(**kwargs)

        self.buffer = None
        self.operations = []

    def run_gifsicle(self):
        '''Mock the run_gifsicle function to return an empty string'''
        return str()


@Vows.batch
class GifEngineVows(Vows.Context):

    class InvalidBuffer(Vows.Context):
        @Vows.capture_error
        def topic(self):
            config = Config()
            context = Context(None, config, Importer(config))
            context.request = RequestParameters()

            engine = MockInvalidResultEngine(context=context)
            return engine.read()

        def should_throw_an_exception(self, topic):
            expect(topic).to_be_an_error()

    class ValidBuffer(Vows.Context):

        def topic(self):
            config = Config()
            server = ServerParameters(
                8889, 'localhost', 'thumbor.conf', None, 'info', None
            )

            context = Context(server, config, Importer(config))
            context.server.gifsicle_path = which('gifsicle')

            context.request = RequestParameters()

            with open("%s/animated_image.gif" % FIXTURES_FOLDER, "rb") as f:
                buffer = f.read()

            engine = GifEngine(context=context)
            engine.load(buffer, '.gif')

            return engine.read()

        def should_generate_a_valid_image(self, topic):
            topic = Image.open(BytesIO(topic))
            topic.verify()
            expect(topic.size).to_equal((290, 360))
