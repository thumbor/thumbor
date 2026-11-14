# Format

Usage: `format(image-format)`

## Description

This filter specifies the output format of the image. The output must be one of:
"webp", "jpeg", "gif", "png", "avif", "heic" or "jxl".

"jxl" needs a Pillow plugin for JPEG XL, as described in
{ref}`jpeg-xl-configuration`. Without one the image keeps the format of its
source. An animated GIF or WebP is not converted to "jxl".

## Arguments

- `image-format` - The output format of the resulting image.

## Example

```
http://localhost:8888/unsafe/filters:format(webp)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
```
