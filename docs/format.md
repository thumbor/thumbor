# Format

Usage: `format(image-format)`

## Description

This filter specifies the output format of the image. The output must be one of:
"webp", "jpeg", "gif", "png", "avif" or "heic".

The `FORMAT_FILTER_ALLOWED_CONVERSIONS` option can limit the output formats
allowed for each source format; see {doc}`configuration`. A conversion it does
not allow is answered with `400 Bad Request`.

## Arguments

- `image-format` - The output format of the resulting image.

## Example

```
http://localhost:8888/unsafe/filters:format(webp)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
```
