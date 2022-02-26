Rotate
======

Usage: `rotate(angle)`

Description
-----------

This filter rotates the given image according to the angle value passed.

.. note::
    This filter rotates the image according to the engine.
    For the PIL engine the rotation is done counter-clockwise.

Arguments
---------

- ``angle`` - ``0 to 359`` - The euler angle to rotate the image by. Numbers greater or equal than 360 will be transformed to a equivalent angle between 0 and 359.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the rotate filter

::

    http://localhost:8888/unsafe/filters:rotate(90)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. image:: images/tom_after_rotate.jpg
    :alt: Picture after the 90 degrees rotate
