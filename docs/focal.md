# Focal

Usage: `focal(<left>x<top>:<right>x<bottom>)`

## Description

This filter adds a focal point, which is used in later transforms.

## Arguments

- `left, top, right, bottom`: All mandatory arguments in the
  `<left>x<top>:<right>x<bottom>` format.

## Example

Before cropping with specific focal point:

```{image} images/tom_before_brightness.jpg
---
alt: Original picture
---
```

```
http://localhost:8888/unsafe/400x100/filters:focal(146x206:279x360)/<url>
```

After specifying the focal point:

```{image} images/after-focal.jpg
---
alt: Picture after the RGB filter
---
```

```{warning}
When using this filter together with detectors, the extract focal points filter,
or the metadata parameter, unexpected behavior may occur.
```
