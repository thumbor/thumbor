Stretch
=======

Usage: `stretch()`

Description
-----------

This filter stretches the image until it fits the required width and height, instead of cropping the image.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the stretch filter

::

    http://localhost:8888/unsafe/200x100/filters:stretch()/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. image:: images/stretch_after.jpg
    :alt: Picture after the stretch filter
