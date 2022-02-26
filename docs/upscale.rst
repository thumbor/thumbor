Upscale
=======

Usage: `upscale()`

Description
-----------

This filter tells thumbor to upscale your images. This only makes sense with
"fit-in" or "adaptive-fit-in".

This means that if an original image is :math:`300px` width by :math:`200px` height and you
ask for a :math:`600x500` image, the filter will resize it to :math:`600x400`.

Arguments
---------

No arguments allowed.

Example
-------

::

    http://localhost:8888/unsafe/fit-in/600x500/filters:upscale()/https://raw.githubusercontent.com/thumbor/thumbor/e86324e49d7e53acc2a8057e43f3fdd2ca5cea75/docs/images/dice_transparent_background.png
