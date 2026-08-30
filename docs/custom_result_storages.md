# Custom Result Storages

Thumbor imports a class named `Storage` from the module configured by
`RESULT_STORAGE` and instantiates it with the current request context:

```python
RESULT_STORAGE = "my_package.result_storage"
```

Custom result storages should inherit from
`thumbor.result_storages.BaseStorage`. The current interface is:

```python
from thumbor.result_storages import BaseStorage, ResultStorageResult


class Storage(BaseStorage):
    async def put(self, image_bytes):
        """Store the generated image for self.context.request."""

    async def get(self):
        """Return a ResultStorageResult, or None on a cache miss."""
```

`get` should return `None` when no valid cached result exists. On a cache hit,
return `ResultStorageResult(buffer=..., metadata=...)`. Metadata may include
`LastModified`, `ContentType` and `ContentLength`; Thumbor derives missing
content type and length information when possible.

`last_updated` is only consulted for compatibility when a backend returns raw
bytes and conditional response headers are enabled. New implementations should
return freshness information as `LastModified` metadata in
`ResultStorageResult`.

`validate_path` and `normalize_path` are helpers used by the built-in file
storage, not required methods for remote or key-value result storages. Whatever
backend is used, derive the key from `self.context.request` and apply the
automatic-format isolation rules below before either reading or writing.

## Automatic image formats and cache keys

A result storage must keep responses for different automatic image-format
capabilities in separate cache namespaces. This is required both for the
individual `AUTO_*` options and for `AUTO_IMAGE_FORMAT_PREFERENCE`. Otherwise,
clients requesting the same thumbor URL but advertising different formats can
receive an incompatible cached image.

Use thumbor's cache-key helper when building the normalized path or key:

```python
from thumbor.auto_image_format import get_auto_image_format_cache_key

format_key = get_auto_image_format_cache_key(
    self.context.config,
    self.context.request,
)
cache_namespace = format_key or "default"

# Include cache_namespace in the complete backend key used by both get() and
# put(). Do not use it as the key by itself.
```

Treat the returned value as an opaque discriminator. It represents the active
automatic formats accepted by the request and can contain more than one format.
For configurations that require isolation from legacy cache entries, it also
contains an internal namespace version. In that mode the helper returns a
discriminator even when no configured format was accepted. Include it in both
read and write keys before any cache lookup.

If a custom handler overrides `BaseHandler.accepts_mime_type` while `AUTO_AVIF`,
`AUTO_HEIF`, `AUTO_JPG`, `AUTO_PNG` or a preference containing one of those
formats is active, thumbor bypasses result storage for that request. The
override may depend on the image engine, filters or other state that does not
exist during the pre-load cache lookup, so no safe cache discriminator can be
calculated at that point. The override continues to run during output-format
selection, at the same stage as before. The same bypass applies to request
objects built by custom handler code without the parsed `accepts_*` attributes:
their format decisions fall back to reading the Accept header, so no cache key
computed from the missing attributes could be trusted. `AUTO_WEBP`-only and
`AUTO_PNG_TO_JPG`-only configurations are unaffected because this hook has never
controlled those conversions.

When enabling or reordering `AUTO_IMAGE_FORMAT_PREFERENCE`, an entry from an
older `default` or `auto_webp` namespace is not necessarily valid for the new
namespace. Treat such an entry as a cache miss and regenerate it. Do not copy or
move legacy objects into a new format namespace unless their actual content type
has been verified. Existing custom storages that do not use the helper must
adopt it before enabling these automatic formats. Purge their generated-image
cache once during that rollout; purging without first isolating the new keys
does not prevent future format collisions.
