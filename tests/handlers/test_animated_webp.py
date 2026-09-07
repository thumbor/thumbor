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


def encode(frames, file_format="WEBP", **options):
    with BytesIO() as stream:
        frames[0].save(
            stream,
            file_format,
            save_all=len(frames) > 1,
            append_images=frames[1:],
            lossless=True,
            **options,
        )
        return stream.getvalue()


def bordered_frames():
    frames = []
    for color in ("red", "green", "blue"):
        frame = Image.new("RGB", (200, 100), "white")
        frame.paste(color, (50, 25, 150, 75))
        frames.append(frame)
    return frames


class AnimatedWebPTestCase(TestCase):
    def setUp(self):
        # Keep the directory alive through asynchronous requests and tearDown.
        # pylint: disable-next=consider-using-with
        self.source_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.source_directory.cleanup)
        root = Path(self.source_directory.name)
        (root / "animated.webp").write_bytes(animation_bytes())
        (root / "animated.gif").write_bytes(animation_bytes("GIF"))
        exif = Image.Exif()
        exif[274] = 6
        (root / "rotated.webp").write_bytes(
            animation_bytes(exif=exif.tobytes())
        )
        opaque = [
            im.convert("RGB") for im in decoded_frames(animation_bytes())
        ]
        (root / "opaque.webp").write_bytes(encode(opaque, duration=DURATIONS))
        (root / "opaque-first.webp").write_bytes(encode(opaque[:1]))
        (root / "page.png").write_bytes(
            encode([Image.new("RGB", (128, 64), "white")], "PNG")
        )
        (root / "bordered.webp").write_bytes(
            encode(bordered_frames(), duration=DURATIONS)
        )
        (root / "translucent.webp").write_bytes(
            encode([Image.new("RGBA", (16, 16), (255, 0, 0, 128))])
        )
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
    async def test_http_respects_orientation_of_every_frame(self):
        self.config.RESPECT_ORIENTATION = True
        response = await self.async_fetch("/unsafe/rotated.webp")
        assert response.code == 200
        frames = decoded_frames(response.body)
        assert [im.size for im in frames] == [(32, 64)] * 3
        response = await self.async_fetch("/unsafe/meta/rotated.webp")
        source = json.loads(response.body)["thumbor"]["source"]
        assert (source["width"], source["height"]) == (32, 64)

    @gen_test
    async def test_auto_format_does_not_flatten_webp_animation(self):
        self.config.AUTO_JPG = True
        self.config.AUTO_PNG = True
        response = await self.async_fetch(
            "/unsafe/animated.webp",
            headers={"Accept": "image/jpeg,image/png"},
        )
        assert response.code == 200
        assert response.headers["Content-Type"] == "image/webp"
        assert len(decoded_frames(response.body)) == 3
        assert "Vary" not in response.headers

    @gen_test
    async def test_static_webp_output_keeps_vary_header(self):
        self.config.AUTO_JPG = True
        response = await self.async_fetch(
            "/unsafe/filters:quality(80)/translucent.webp",
            headers={"Accept": "image/jpeg"},
        )
        assert response.code == 200
        assert response.headers["Content-Type"] == "image/webp"
        assert response.body[12:16] == b"VP8X"
        assert response.headers["Vary"] == "Accept"

    @gen_test
    async def test_animated_watermark_uses_its_transformed_first_frame(self):
        url = "/unsafe/filters:watermark({},0,0,50,100,100)/page.png"
        animated = await self.async_fetch(url.format("opaque.webp"))
        static = await self.async_fetch(url.format("opaque-first.webp"))
        assert animated.code == static.code == 200
        frame = decoded_frames(animated.body)[0]
        assert frame.tobytes() == decoded_frames(static.body)[0].tobytes()
        assert frame.getpixel((0, 0)) != (255, 255, 255, 255)

    @gen_test
    async def test_trim_after_normalize_matches_the_first_frame(self):
        self.config.MAX_WIDTH = 100
        self.config.MAX_HEIGHT = 100
        self.config.ALLOW_ANIMATED_WEBP = False
        static = await self.async_fetch("/unsafe/trim/bordered.webp")
        self.config.ALLOW_ANIMATED_WEBP = True
        animated = await self.async_fetch("/unsafe/trim/bordered.webp")
        assert static.code == animated.code == 200
        expected = decoded_frames(static.body)[0]
        frames = decoded_frames(animated.body)
        assert expected.width < 100 and expected.height < 50
        assert [im.size for im in frames] == [expected.size] * 3
        assert frames[0].tobytes() == expected.tobytes()

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
