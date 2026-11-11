# Upscale

Usage: `upscale()`

## Description

This filter tells thumbor to upscale your images. This only makes sense with
"fit-in" or "adaptive-fit-in".

This means that if an original image is $300px$ width by $200px$ height and you
ask for a $600x500$ image, the filter will resize it to $600x400$.

A dimension left out or given as $0$ follows the other one proportionally, so
$600x$ on that image gives $600x400$ as well. A dimension given as "orig"
keeps the original size on that axis, so the filter leaves the image as it is.

## Arguments

No arguments allowed.

## Example

```
http://localhost:8888/unsafe/fit-in/600x500/filters:upscale()/https://raw.githubusercontent.com/thumbor/thumbor/e86324e49d7e53acc2a8057e43f3fdd2ca5cea75/docs/images/dice_transparent_background.png
```
