# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from os.path import abspath, dirname, join
from shutil import which

from PIL import Image

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import RequestParameters, ServerParameters
from thumbor.engines.gif import Engine
from thumbor.importer import Importer

STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class GifEngineTestCase(TestCase):
    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines.gif",
            IMAGE_METADATA_READ_FORMATS="exif,xmp",
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=STORAGE_PATH,
            STORAGE="thumbor.storages.no_storage",
            USE_GIFSICLE_ENGINE=True,
            RESPECT_ORIENTATION=True,
        )

    def get_importer(self):
        return Importer(self.config)

    def get_server(self):
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        server.gifsicle_path = which("gifsicle")
        return server

    def get_context(self):
        context = super().get_context()
        req = RequestParameters(url="/foo/bar.gif")
        context.request = req
        return context

    def test_create_engine(self):
        engine = Engine(self.context)
        assert isinstance(engine, Engine)

    def test_load_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()
        image = engine.create_image(buffer)
        assert image.format == "GIF"

    def test_errors_on_gifsicle_should_not_raises_errors_when_output(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "SmallFullColourGIF.gif"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, ".gif")
        result = engine.run_gifsicle("--some-invalid-opt")
        assert result is not None

    def load_animated_gif(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            engine.load(image_file.read(), ".gif")
        return engine

    def test_resize_passes_integer_dimensions_to_gifsicle(self):
        engine = self.load_animated_gif()

        engine.resize(70.0, 50.9)
        engine.resize(70.0, 0)
        engine.resize(0, 50.9)
        engine.resize(0.0, 0.0)

        assert engine.operations == [
            "--resize 70x50",
            "--resize-width 70",
            "--resize-height 50",
        ]

    def test_crop_passes_integer_coordinates_to_gifsicle(self):
        engine = self.load_animated_gif()

        engine.crop(1.0, 2.5, 30.0, 40.9)

        assert tuple(engine.size) == (29, 38)

    def test_read_resizes_with_float_dimensions(self):
        engine = self.load_animated_gif()

        engine.resize(70.0, 70.0)
        result = engine.read(".gif")

        assert Image.open(BytesIO(result)).size == (70, 70)

    def test_is_multiple_should_returns_true_if_gif_has_many_frames(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()

        engine.load(buffer, ".gif")
        assert engine.is_multiple()

    def test_is_multiple_should_returns_false_if_gif_has_one_frame(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "animated-one-frame.gif"), "rb"
        ) as image_file:
            buffer = image_file.read()

        engine.load(buffer, ".gif")
        assert not engine.is_multiple()

    def test_convert_to_grayscale_should_update_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()

        engine.load(buffer, ".gif")
        buffer = engine.read()
        engine.convert_to_grayscale()

        assert buffer != engine.read()

    def test_convert_to_grayscale_should_not_update_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "animated.gif"), "rb") as image_file:
            buffer = image_file.read()

        engine.load(buffer, ".gif")
        buffer = engine.read()
        engine.convert_to_grayscale(False)

        assert buffer == engine.read()
