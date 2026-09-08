# Saturation

Usage: `saturation(amount)`

## Description

This filter increases or decreases the image saturation.

## Arguments

- `amount` - $-100$ to $100$ - The amount (in %) to change the image saturation.
  Positive numbers increase saturation and negative numbers decrease saturation.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the saturation filter
---
```

http://localhost:8888/unsafe/filters:saturation(40)/<url>

```{image} images/tom_after_positive_saturation.jpg
---
alt: Picture after positive saturation
---
```

http://localhost:8888/unsafe/filters:saturation(-40)/<url>

```{image} images/tom_after_negative_saturation.jpg
---
alt: Picture after negative saturation
---
```
