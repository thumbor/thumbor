# Noise

Usage: `noise(amount)`

## Description

This filter adds noise to the image.

## Arguments

- `amount` - `0% to 100%` - The amount of noise to add to the image.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the noise filter
---
```

```
http://localhost:8888/unsafe/filters:noise(40)/<url>
```

```{image} images/tom_after_noise.jpg
---
alt: Picture after noise of 40%
---
```
