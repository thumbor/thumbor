# Brightness

Usage: `brightness(amount)`

## Description

This filter increases or decreases the image brightness.

## Arguments

- `amount` - `-100 to 100` - The amount (in %) to change the image brightness.
  Positive numbers make the image brighter and negative numbers make the image
  darker.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the brightness
---
```

```
http://localhost:8888/unsafe/filters:brightness(40)/<url>
```

```{image} images/tom_after_brightness.jpg
---
alt: Picture after the brightness
---
```
