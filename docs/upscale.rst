Upscale
=======

Usage: upscale()

Description
-----------

This filter tells thumbor to upscale your images. This only makes sense with
"fit-in" or "adaptive-fit-in".

This means that if an original image is 300px width by 200px height and you
ask for a 600x500 image, the filter will resize it to 600x400.

Arguments
---------

No arguments allowed.

Example
-------

`<http://localhost:8888/unsafe/fit-in/600x500/filters:upscale()/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_
