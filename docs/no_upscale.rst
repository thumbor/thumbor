No upscale
==========

Usage: no_upscale()

Description
-----------

This filter tells thumbor not to upscale your images.

This means that if an original image is 300px width by 200px height and
you ask for a 600x400 image, thumbor will still return a 300x200 image.

Arguments
---------

No arguments allowed.

Example
-------

`<http://thumbor-server/unsafe/300x200/filters:no_upscale()/some/image.jpg>`_
