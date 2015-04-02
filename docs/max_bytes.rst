Max bytes
=========

Usage: max\_bytes(number-of-bytes)

Description
-----------

This filter automatically degrades the quality of the image until the
image is under the specified amount of bytes.

Arguments
---------

number-of-bytes - The maximum number of bytes for the given image.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the max_bytes filter

`<http://thumbor-server/filters:max_bytes(40000)/some/image.jpg>`_

.. image:: images/tom_after_max_bytes.jpg
    :alt: Picture after 10000 max_bytes filter
