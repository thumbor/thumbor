No upscale
==========

Usage: `no_upscale()`

Description
-----------

This filter tells thumbor not to upscale your images.

This means that if an original image is :math:`300px` width by :math:`200px` height and
you ask for a :math:`600x400` image, thumbor will still return a :math:`300x200` image.

Arguments
---------

No arguments allowed.

Example
-------

::

    http://localhost:8888/unsafe/filters:no_upscale()/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
