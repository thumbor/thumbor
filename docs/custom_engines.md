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

    def read(self, extension, quality):
        """Encode and return the final image bytes."""
```

`BaseEngine.load()` handles extension detection, SVG conversion, EXIF metadata
and animated-frame setup before calling `create_image()`. Reuse it unless your
format requires a different loading lifecycle.

A production engine must also implement the operations used by the filters and
features it supports. These can include `gen_image`, `rotate`,
`image_data_as_rgb`, `get_image_data`, `set_image_data`, `get_image_mode`,
`paste`, `enable_alpha`, `convert_to_grayscale`, `draw_rectangle`,
`extract_cover`, `has_transparency`, `avif_enabled`, `heif_enabled` and
`read_multiple`. Unsupported optional operations should fail explicitly or be
paired with configuration that prevents the corresponding feature from being
selected.

The active request and configuration are available through `self.context`. If
the engine owns native or temporary resources, override `cleanup()`; Thumbor
calls it during request cleanup.

Use `thumbor.engines.pil.Engine` as the reference implementation. Test at least
load/read round trips, crop, resize, orientation, transparency, malformed
input, animated input if supported, and every automatic output format the
engine advertises.
