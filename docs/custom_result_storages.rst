Custom Result Storages
======================

In order to implement your own result storage, you have to implement a
few methods. A reference implementation can be found at the `File
Storage <https://github.com/thumbor/thumbor/blob/master/thumbor/result_storages/file_storage.py>`__.

The required methods are ``put``, ``get``, ``validate_path`` and
``normalize_path``.

Automatic image formats and cache keys
--------------------------------------

A result storage must keep responses for different automatic image-format
capabilities in separate cache namespaces. This is required for the
individual ``AUTO_*`` options. Otherwise, clients requesting the same
thumbor URL but advertising different formats can receive an incompatible
cached image.

Use thumbor's cache-key helper when building the normalized path or key:

.. code:: python

   from thumbor.auto_image_format import get_auto_image_format_cache_key

   format_key = get_auto_image_format_cache_key(
       self.context.config,
       self.context.request,
   )
   cache_namespace = format_key or "default"

Treat the returned value as an opaque discriminator. It represents the
active automatic formats accepted by the request and can contain more than
one format. For configurations that require isolation from legacy cache
entries, it also contains an internal namespace version. In that mode the
helper returns a discriminator even when no configured format was accepted.
Include it in both read and write keys before any cache lookup.

If a custom handler overrides ``BaseHandler.accepts_mime_type`` while
``AUTO_AVIF``, ``AUTO_HEIF``, ``AUTO_JPG`` or ``AUTO_PNG`` is active,
thumbor bypasses result storage for that request. The override may depend
on the image engine, filters or other state that does not exist during the
pre-load cache lookup, so no safe cache discriminator can be calculated at
that point. The override continues to run during output-format selection,
at the same stage as before. The same bypass applies to request objects
built by custom handler code without the parsed ``accepts_*`` attributes:
their format decisions fall back to reading the Accept header, so no cache
key computed from the missing attributes could be trusted.
``AUTO_WEBP``-only and ``AUTO_PNG_TO_JPG``-only configurations are
unaffected because this hook has never controlled those conversions.

An entry from an older ``default`` or ``auto_webp`` namespace is not
necessarily valid for the new namespace. Treat such an entry as a cache
miss and regenerate it. Do not copy or move legacy objects into a new
format namespace unless their actual content type has been verified.
Existing custom storages that do not use the helper must adopt it before
enabling these automatic formats. Purge their generated-image cache once
during that rollout; purging without first isolating the new keys does not
prevent future format collisions.
