import json
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image
from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.animated_webp import (
    DURATIONS,
    animation_bytes,
    decoded_frames,
)
from thumbor.config import Config


class AnimatedWebPTestCase(TestCase):
    def setUp(self):
        # Keep the directory alive through asynchronous requests and tearDown.
        # pylint: disable-next=consider-using-with
        self.source_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.source_directory.cleanup)
        root = Path(self.source_directory.name)
        (root / "animated.webp").write_bytes(animation_bytes())
        (root / "animated.gif").write_bytes(animation_bytes("GIF"))
        super().setUp()

    def get_config(self):
        return Config(
            SECURITY_KEY="ACME-SEC",
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=self.source_directory.name,
            STORAGE="thumbor.storages.no_storage",
            RESULT_STORAGE="thumbor.result_storages.no_storage",
            QUALITY=100,
        )

    @gen_test
    async def test_http_preserves_animation_through_resize_and_grayscale(self):
        for operations, size, grayscale in (
            ("", (64, 32), False),
            ("50x0/", (50, 25), False),
            ("filters:grayscale()/", (64, 32), True),
            ("50x0/filters:grayscale()/", (50, 25), True),
        ):
            with self.subTest(operations=operations):
                response = await self.async_fetch(
                    f"/unsafe/{operations}animated.webp"
                )
                assert response.code == 200
                assert response.headers["Content-Type"] == "image/webp"
                with Image.open(BytesIO(response.body)) as image:
                    assert image.n_frames == 3
                    assert image.info["loop"] == 2
                frames = decoded_frames(response.body)
                assert [im.size for im in frames] == [size] * 3
                assert [im.info["duration"] for im in frames] == DURATIONS
                if grayscale:
                    for frame in frames:
                        red, green, blue, alpha = frame.split()
                        assert (
                            red.tobytes() == green.tobytes() == blue.tobytes()
                        )
                        assert alpha.getextrema()[0] < 255

    @gen_test
    async def test_http_metadata_reports_all_frames(self):
        response = await self.async_fetch("/unsafe/meta/animated.webp")
        assert response.code == 200
        assert (
            json.loads(response.body)["thumbor"]["source"]["frameCount"] == 3
        )

    @gen_test
    async def test_auto_format_does_not_flatten_webp_animation(self):
        self.config.AUTO_JPG = True
        response = await self.async_fetch(
            "/unsafe/animated.webp", headers={"Accept": "image/jpeg"}
        )
        assert response.code == 200
        assert response.headers["Content-Type"] == "image/webp"
        assert len(decoded_frames(response.body)) == 3

    @gen_test
    async def test_gif_control_retains_frames_after_resize(self):
        response = await self.async_fetch("/unsafe/32x0/animated.gif")
        assert response.code == 200
        frames = decoded_frames(response.body)
        assert len(frames) == 3
        for frame in frames:
            assert frame.size == (32, 16)

    @gen_test
    async def test_encoder_failure_returns_an_error_instead_of_a_static_image(
        self,
    ):
        with patch.dict(
            Image.SAVE_ALL,
            {"WEBP": Mock(side_effect=OSError("encoder unavailable"))},
        ):
            response = await self.async_fetch("/unsafe/animated.webp")
        assert response.code == 500
