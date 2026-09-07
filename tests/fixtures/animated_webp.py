"""Small synthetic animations with distinct colors, alpha and frame delays."""

from io import BytesIO

from PIL import Image

DURATIONS = [80, 130, 210]


def animation_bytes(file_format="WEBP", loop=2, **metadata):
    frames = []
    for channel in range(3):
        frame = Image.new("RGBA", (64, 32))
        pixels = []
        for y in range(32):
            for x in range(64):
                color = [x * 3, y * 7, (x + y) * 2, 128 + (x % 2) * 127]
                color[channel] = 255
                pixels.append(tuple(color))
        frame.putdata(pixels)
        frames.append(frame)
    with BytesIO() as stream:
        frames[0].save(
            stream,
            file_format,
            save_all=True,
            append_images=frames[1:],
            duration=DURATIONS,
            loop=loop,
            lossless=True,
            **metadata,
        )
        return stream.getvalue()


def decoded_frames(data):
    with Image.open(BytesIO(data)) as image:
        frames = []
        for index in range(image.n_frames):
            image.seek(index)
            frames.append(image.convert("RGBA"))
        return frames
