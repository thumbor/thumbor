from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from PIL import Image, ImageCms

from tests.fixtures.animated_webp import (
    DURATIONS,
    animation_bytes,
    decoded_frames,
)
from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def load_engine(data, **settings):
    engine = Engine(Context(config=Config(**settings)))
    engine.load(data, None)
    return engine


@pytest.mark.parametrize("loop", [0, 2])
@pytest.mark.parametrize("allow_gifs", [True, False])
def test_webp_roundtrip_preserves_frames_timing_and_loop(loop, allow_gifs):
    source = animation_bytes(loop=loop)
    engine = load_engine(source, ALLOW_ANIMATED_GIFS=allow_gifs)
    assert engine.is_multiple()
    assert engine.frame_count == 3
    result = engine.read(quality=100)
    with Image.open(BytesIO(result)) as image:
        assert image.format == "WEBP"
        assert image.n_frames == 3
        assert image.info["loop"] == loop
    actual = decoded_frames(result)
    assert [frame.info["duration"] for frame in actual] == DURATIONS
    assert [frame.tobytes() for frame in actual] == [
        frame.tobytes() for frame in decoded_frames(source)
    ]


@pytest.mark.parametrize("durations", [[0, 0, 0], [0, 80, 0]])
def test_webp_roundtrip_preserves_zero_duration_frames(durations):
    source = animation_bytes(duration=durations)
    engine = load_engine(source)
    assert engine.is_multiple()
    assert engine.frame_count == 3

    actual = decoded_frames(engine.read(quality=100))
    assert len(actual) == 3
    assert [frame.info["duration"] for frame in actual] == durations
    assert [frame.tobytes() for frame in actual] == [
        frame.tobytes() for frame in decoded_frames(source)
    ]


@pytest.mark.parametrize(
    "operation", ["resize", "crop", "flip_horizontally", "flip_vertically"]
)
def test_webp_transforms_every_frame(operation):
    source = animation_bytes()
    engine = load_engine(source, QUALITY=100)
    expected = decoded_frames(source)
    if operation == "resize":
        engine.resize(32, 16)
        expected = [
            im.resize((32, 16), Image.Resampling.LANCZOS) for im in expected
        ]
    elif operation == "crop":
        engine.crop(4, 2, 44, 22)
        expected = [im.crop((4, 2, 44, 22)) for im in expected]
    else:
        getattr(engine, operation)()
        transpose = (
            Image.Transpose.FLIP_LEFT_RIGHT
            if operation == "flip_horizontally"
            else Image.Transpose.FLIP_TOP_BOTTOM
        )
        expected = [im.transpose(transpose) for im in expected]
    actual = decoded_frames(engine.read())
    assert len(actual) == 3
    assert [im.size for im in actual] == [im.size for im in expected]
    assert [im.tobytes() for im in actual] == [im.tobytes() for im in expected]
    assert [im.info["duration"] for im in actual] == DURATIONS


def test_webp_animation_can_be_disabled_independently():
    source = animation_bytes()
    engine = load_engine(source, ALLOW_ANIMATED_WEBP=False)
    assert not engine.is_multiple()
    actual = decoded_frames(engine.read(quality=100))
    assert len(actual) == 1
    assert actual[0].tobytes() == decoded_frames(source)[0].tobytes()
    gif = load_engine(animation_bytes("GIF"), ALLOW_ANIMATED_WEBP=False)
    assert gif.is_multiple()


def test_static_webp_keeps_the_single_image_path():
    with BytesIO() as stream:
        Image.new("RGB", (16, 16), "red").save(stream, "WEBP")
        engine = load_engine(stream.getvalue())
    assert not engine.is_multiple()
    assert len(decoded_frames(engine.read())) == 1


@pytest.mark.parametrize("extension", [".jpg", ".png"])
def test_explicit_static_conversion_uses_the_transformed_first_frame(
    extension,
):
    engine = load_engine(animation_bytes())
    engine.resize(32, 16)
    with Image.open(BytesIO(engine.read(extension=extension))) as image:
        assert getattr(image, "n_frames", 1) == 1
        assert image.size == (32, 16)


def test_webp_animation_is_enabled_by_default():
    assert Config().ALLOW_ANIMATED_WEBP is True


def test_encoder_failure_does_not_return_a_static_fallback():
    engine = load_engine(animation_bytes())
    with patch.dict(
        Image.SAVE_ALL,
        {"WEBP": Mock(side_effect=OSError("encoder unavailable"))},
    ):
        with pytest.raises(OSError, match="encoder unavailable"):
            engine.read()


@pytest.mark.parametrize("strip", [False, True])
def test_animation_respects_metadata_preservation_and_strip_operations(strip):
    profile = ImageCms.ImageCmsProfile(
        ImageCms.createProfile("sRGB")
    ).tobytes()
    exif = Image.Exif()
    exif[270] = "Synthetic animation"
    source = animation_bytes(icc_profile=profile, exif=exif.tobytes())
    engine = load_engine(source, PRESERVE_EXIF_INFO=True)
    if strip:
        for frame_engine in engine.frame_engines():
            frame_engine.strip_icc()
            frame_engine.strip_exif()
    with Image.open(BytesIO(engine.read())) as result:
        assert result.n_frames == 3
        if strip:
            assert "icc_profile" not in result.info
            assert not result.getexif()
        else:
            assert result.info["icc_profile"] == profile
            assert result.getexif()[270] == "Synthetic animation"
