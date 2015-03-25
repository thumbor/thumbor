Rotate
======

Usage: rotate(angle)

Description
-----------

This filter rotate the given image according to the angle value passed.

Arguments
---------

angle - 0 to 359 - The angle to rotate the image. Numbers greater or
equal than 360 will be tranformed to a equivalent angle between 0 and
359.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the rotate filter

`<http://thumbor-server/filters:rotate(90)/some/image.jpg>`_

.. image:: images/tom_after_rotate.jpg
    :alt: Picture after the 90 degrees rotate

