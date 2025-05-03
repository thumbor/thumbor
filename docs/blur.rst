Blur
====

Usage: `blur(radius [, sigma])`

Description
-----------

This filter applies a gaussian blur to the image.

Arguments
---------

-  ``radius`` - Radius used in the gaussian function to generate a matrix,
   maximum value is 150. The bigger the radius more blurred will be the
   image.
-  ``sigma`` - Optional. Defaults to the same value as the radius. Sigma
   used in the gaussian function.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the blur filter

::

    http://localhost:8888/unsafe/filters:blur(7)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. image:: images/tom_after_blur.jpg
    :alt: Picture after the blur filter
