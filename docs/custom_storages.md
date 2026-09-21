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
loading calls `get` and, after a miss, `put` followed by `put_crypto`.
`put_crypto` is called even when `STORES_CRYPTO_KEY_FOR_EACH_IMAGE` is
disabled, so it must exist at least as a no-op that returns `None`, as the
built-in file storage does. The upload `/image/<id>` routes use `exists`, `get`
and `remove`, and the blacklist handlers use `exists`, `get` and `put`.
Per-image signing reads the key back with `get_crypto`, and smart detection
uses `get_detector_data` and `put_detector_data`.

The request context is available as `self.context`, including
`self.context.config`, `self.context.request` and `self.context.server`. See
`thumbor/storages/file_storage.py` for the built-in reference implementation.

Storage methods run on Thumbor's event loop. Avoid blocking network or disk
operations in an `async` method; use an asynchronous client or explicitly move
blocking work off the event loop.
