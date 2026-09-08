# Contrast

Usage: `contrast(amount)`

## Description

This filter increases or decreases the image contrast.

## Arguments

- `amount` - $-100$ to $100$ - The amount (in %) to change the image contrast.
  Positive numbers increase contrast and negative numbers decrease contrast.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the contrast filter
---
```

```
http://localhost:8888/unsafe/filters:contrast(40)/<url>
```

```{image} images/tom_after_positive_contrast.jpg
---
alt: Picture after positive contrast
---
```

```
http://localhost:8888/unsafe/filters:contrast(-40)/<url>
```

```{image} images/tom_after_negative_contrast.jpg
---
alt: Picture after negative contrast
---
```
