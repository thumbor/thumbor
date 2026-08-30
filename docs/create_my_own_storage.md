# Creating an Upload Storage

The upload API writes new and replacement images through the module configured
by `UPLOAD_PHOTO_STORAGE`. Thumbor imports a class named `Storage` from that
module and instantiates it with the current request context.

An upload storage should inherit from `thumbor.storages.BaseStorage` and
implement an asynchronous `put` method:

```python
from thumbor.storages import BaseStorage


class Storage(BaseStorage):
    async def put(self, path, file_bytes):
        """Store file_bytes under path."""
```

Configure the module name, without the `.Storage` class suffix:

```python
UPLOAD_PHOTO_STORAGE = "my_package.upload_storage"
```

The module must be importable in the Python environment that runs Thumbor.
`ORIGINAL_PHOTO_STORAGE` remains a compatibility alias, but new configurations
should use `UPLOAD_PHOTO_STORAGE`.

The built-in `/image/<id>` retrieval and deletion handlers use the main
`STORAGE`, not `UPLOAD_PHOTO_STORAGE`. To manage uploaded images through those
routes, configure compatible backends for both settings. If the same module is
used as the main `STORAGE`, it must also implement `get`, `exists`, `remove`
and the metadata operations required by the enabled storage features. See the
custom storage documentation for that complete interface.
