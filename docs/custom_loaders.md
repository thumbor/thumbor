# Custom Image Loaders

If thumbor's image loaders do not meet your needs, you can implement a custom
loader as an importable Python module.

A loader module must expose an asynchronous `load(context, url)` function.
`context` is the current request context, and `url` is the source-image path
from the thumbor request. New loaders should return a
`thumbor.loaders.LoaderResult`.

```python
from thumbor.loaders import LoaderResult


async def load(context, url):
    image_bytes = context.config.MY_LOADER_IMAGES.get(url)

    if image_bytes is None:
        return LoaderResult(
            successful=False,
            error=LoaderResult.ERROR_NOT_FOUND,
        )

    return LoaderResult(buffer=image_bytes)
```

For compatibility, thumbor still accepts raw image bytes returned by old
loaders, but new loaders should return `LoaderResult` so they can report errors
and metadata explicitly.

A loader may also expose a synchronous `validate(context, url)` function.
Thumbor calls it before loading the image. Return `True` to accept the URL and
`False` to reject it.

```python
def validate(context, url):
    return url.startswith("images/")
```

Configure the loader using its module name:

```python
MY_LOADER_IMAGES = {
    "images/example.jpg": b"...",
}
LOADER = "mylib.loaders.custom_loader"
```

The HTTP loader at `thumbor/loaders/http_loader.py` and the filesystem loader
at `thumbor/loaders/file_loader.py` are reference implementations.
