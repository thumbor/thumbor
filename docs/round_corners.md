# Round corners

Usage: `round_corner(a|b,r,g,b,[transparent])`

## Description

This filter adds rounded corners to the image using the specified color as
background.

## Arguments

- `a|b` - amount of pixels to use as radius. The argument `b` is not required,
  but it specifies the second value for the ellipsis used for the radius.
- `transparent` - Optional. If set to true/1, the background will be
  transparent.

## Examples

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the round corners filter filter
---
```

```
http://localhost:8888/unsafe/filters:round_corner(20,255,255,255)/<url>
```

```{image} images/rounded1.jpg
---
alt: Picture after rounded corners
---
```

```
http://localhost:8888/unsafe/filters:round_corner(20|40,0,0,0)/<url>
```

```{image} images/rounded2.jpg
---
alt: Picture after rounded corners
---
```

```
http://localhost:8888/unsafe/filters:round_corner(30,0,0,0,1)/<url>
```

```{image} images/rounded3.jpg
---
alt: Picture after rounded corners (transparent)
---
```
