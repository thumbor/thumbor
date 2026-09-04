# Filters

## How Filters Work

Thumbor handles filters in a pipeline. This means that they run sequentially in
the order they are specified! Given an original image with size $60x40$ and the
following transformations:

```
http://thumbor/fit-in/100x100/filters:<filter-chain>/<url>
```

The resulting image will first check if it can fit into a $100x100$. Since it
does, the filter pipeline will kick in and:

- add the watermark in the image;
- blur the whole image (including the watermark);
- Fill the outer parts of the image with red (so it will fit in $100x100$);
- Then it will try to upscale. This will have no effect, since at this point the
  image is already $100x100$.

## Available Filters

```{toctree}
---
maxdepth: 1
---
autojpg
background_color
blur
brightness
contrast
convolution
cover
equalize
extract_focal_points
filling
focal
format
grayscale
max_bytes
no_upscale
noise
proportion
quality
red_eye
rgb
rotate
round_corners
saturation
sharpen
stretch
strip_exif
strip_icc
upscale
watermark
```
