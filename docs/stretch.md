# Stretch

Usage: `stretch()`

## Description

This filter stretches the image until it fits the required width and height,
instead of cropping the image.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the stretch filter
---
```

```
http://localhost:8888/unsafe/200x100/filters:stretch()/<url>
```

```{image} images/stretch_after.jpg
---
alt: Picture after the stretch filter
---
```
