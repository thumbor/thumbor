Strip ICC
=========

Usage: `strip\_icc()`

Description
-----------

This filter removes any ICC information in the resulting image. Even
though the image might be smaller, removing ICC information may result
in loss of quality.

Arguments
---------

No arguments

Example
-------

::

    http://localhost:8888/unsafe/filters:strip\_icc()/http://videoprocessing.ucsd.edu/~stanleychan/research/pix/Blurred_foreman_0005.png
