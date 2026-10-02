# Custom Engines

Thumbor imports a class named `Engine` from the module configured by `ENGINE`
and creates an instance with the current request context:

```python
ENGINE = "my_package.engine"
```

Start by subclassing `thumbor.engines.BaseEngine`:

```python
from thumbor.engines import BaseEngine


class Engine(BaseEngine):
    def create_image(self, buffer):
        """Decode buffer and return the backend image object."""

    @property
    def size(self):
        """Return the current (width, height)."""

    def crop(self, left, top, right, bottom):
        """Crop using Thumbor's pixel coordinates."""

    def resize(self, width, height):
        """Resize the current image."""

    def flip_horizontally(self):
        """Flip the current image horizontally."""

    def flip_vertically(self):
        """Flip the current image vertically."""

    def read(self, extension=None, quality=None):
        """Encode and return the final image bytes."""
```

Keep the defaults on `read()`. `BaseEngine` declares both arguments as
required, but the `frame` filter calls `read()` without arguments on a new
instance of the configured engine, as the PIL engine allows.

`BaseEngine.load()` detects the extension and converts SVG input before calling
`create_image()`. After `create_image()` returns, it reads EXIF metadata from
`self.exif` and wraps animated input in per-frame engines. Both steps depend on
`create_image()`: set `self.exif` to the raw EXIF bytes when the format carries
them, and return a list or tuple of frames for animated input so that
`ALLOW_ANIMATED_GIFS` handling applies (`ALLOW_ANIMATED_WEBP` also enables it
for WebP input). Reuse `load()` unless your format requires a different loading
lifecycle.

A production engine must also implement the operations used by the filters and
features it supports. These can include `gen_image`, `rotate`,
`image_data_as_rgb`, `get_image_data`, `set_image_data`, `get_image_mode`,
`paste`, `enable_alpha`, `convert_to_grayscale`, `draw_rectangle`,
`extract_cover`, `has_transparency`, `avif_enabled`, `heif_enabled` and
`read_multiple`. Unsupported optional operations should fail explicitly or be
paired with configuration that prevents the corresponding feature from being
selected.

The active request and configuration are available through `self.context`.
Thumbor creates a new engine for every request and does not call `cleanup()`
when the request ends; it only runs for the server context's engine at
shutdown. Release native or temporary resources inside the operations that
allocate them instead of relying on `cleanup()`.

Use `thumbor.engines.pil.Engine` as the reference implementation. Test at least
load/read round trips, crop, resize, orientation, transparency, malformed
input, animated input if supported, and every automatic output format the
engine advertises.
