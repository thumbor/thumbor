# Custom Storages

A storage persists original images and the metadata Thumbor associates with
them. Configure it with `STORAGE`:

```python
STORAGE = "my_package.storage"
```

Thumbor imports a class named `Storage` from that module and instantiates it
with the current request context. Custom storages should inherit from
`thumbor.storages.BaseStorage`.

The storage interface is asynchronous:

```python
from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    async def put(self, path, file_bytes):
        """Store the original image."""

    async def get(self, path):
        """Return the stored bytes, or None when the image is unavailable."""

    async def exists(self, path):
        """Return whether the original image is available."""

    async def remove(self, path):
        """Remove the original image."""

    async def put_crypto(self, path):
        """Store the signing key associated with the image."""

    async def get_crypto(self, path):
        """Return the signing key associated with the image, or None."""

    async def put_detector_data(self, path, data):
        """Store detector data associated with the image."""

    async def get_detector_data(self, path):
        """Return detector data associated with the image, or None."""
```

Implement every operation used by the features you enable. Normal image
loading uses `put`, `get` and `exists`; uploads and image management also use
`remove`; smart detection and per-image signing use the detector and crypto
methods.

The request context is available as `self.context`, including
`self.context.config`, `self.context.request` and `self.context.server`. See
`thumbor/storages/file_storage.py` for the built-in reference implementation.

Storage methods run on Thumbor's event loop. Avoid blocking network or disk
operations in an `async` method; use an asynchronous client or explicitly move
blocking work off the event loop.
