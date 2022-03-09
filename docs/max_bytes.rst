Max bytes
=========

Usage: `max\_bytes(number-of-bytes)`

Description
-----------

This filter automatically degrades the quality of the image until the
image is under the specified amount of bytes.

Arguments
---------

- ``number-of-bytes`` - The maximum number of bytes for the given image.

Example
-------

Compressing the original image to less than 7.5k (ended up with ~7kb):

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the max_bytes filter

::

    http://localhost:8888/unsafe/filters:max_bytes(7500)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. image:: images/tom_after_max_bytes.jpg
    :alt: Picture after 7500 max_bytes filter
