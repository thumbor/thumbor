# Round corners

Usage: `round_corner(a|b,r,g,b,[transparent])`

## Description

This filter adds rounded corners to the image using the specified color as
background.

## Arguments

- `a|b` - amount of pixels to use as radius. The argument `b` is not required,
  but it specifies the second value for the ellipsis used for the radius.
- `transparent` - Optional. If set to true/1, the background will be
  transparent and the rounded edge is smoothed through the alpha channel. Use
  an output format with alpha, such as PNG, WebP or AVIF. Formats without
  alpha, such as JPEG, show the color in the corners with a hard edge, so omit
  `transparent` there to blend the edge into the color.

## Examples

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the round corners filter filter
---
```

```
http://localhost:8888/unsafe/filters:round_corner(20,255,255,255)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
```

```{image} images/rounded1.jpg
---
alt: Picture after rounded corners
---
```

```
http://localhost:8888/unsafe/filters:round_corner(20|40,0,0,0)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
```

```{image} images/rounded2.jpg
---
alt: Picture after rounded corners
---
```

```
http://localhost:8888/unsafe/filters:round_corner(30,0,0,0,1):format(png)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
```

```{image} images/rounded3.png
---
alt: Picture after rounded corners (transparent)
---
```
