Blur
====

Usage: blur(radius [, sigma])

Description
-----------

This filter applies a gaussian blur to the image.

Arguments
---------

-  radius - Radius used in the gaussian function to generate a matrix,
   maximum value is 150. The bigger the radius more blurred will be the
   image.
-  sigma - Optional. Defaults to the same value as the radius. Sigma
   used in the gaussian function.

Example
-------

.. image:: images/blur_before.jpg
    :alt: Picture before the blur filter

`<http://localhost:8888/unsafe/filters:blur(7)/http://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/2006_Ojiya_balloon_festival_011.jpg/159px-2006_Ojiya_balloon_festival_011.jpg>`_

.. image:: images/blur_after.jpg
    :alt: Picture after the blur filter
