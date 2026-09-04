# Background Color

Usage: `background_color(color)`

## Description

The background_color filter sets the background layer to the specified color.
This is specifically useful when converting transparent images (PNG) to JPEG

## Arguments

- `color` - the color name (like in HTML) or hexadecimal rgb expression without
  the "#" character. See the list of supported
  [web colors](https://en.wikipedia.org/wiki/Web_colors). If color is "auto", a
  color will be smartly chosen based on the image pixels.

## Example

The original image is:

```{image} images/dice_transparent_background.png
---
alt: Original picture
---
```

```
http://localhost:8888/unsafe/fit-in/300x300/filters:background_color(blue)/<url>
```

```{image} images/dice_blue_background.png
---
alt: Picture after the background_color(blue) filter
---
```

```
http://localhost:8888/unsafe/fit-in/300x300/filters:background_color(f00)/<url>
```

```{image} images/dice_red_background.png
---
alt: Picture after the background_color(f00) filter
---
```

```
http://thumbor/unsafe/fit-in/300x300/filters:background_color(add8e6)/<url>
```

```{image} images/dice_lightblue_background.png
---
alt: Picture after the background_color(add8e6)
---
```
