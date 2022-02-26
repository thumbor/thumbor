RGB
===

Usage: `rgb(rAmount, gAmount, bAmount)`

Description
-----------

This filter changes the amount of color in each of the three channels.

Arguments
---------

-  ``rAmount`` - The amount of redness in the picture. Can range from -100
   to 100 in percentage.
-  ``gAmount`` - The amount of greenness in the picture. Can range from -100
   to 100 in percentage.
-  ``bAmount`` - The amount of blueness in the picture. Can range from -100
   to 100 in percentage.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the RGB filter

::

    http://localhost:8888/unsafe/filters:rgb(20,-20,40)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. image:: images/tom_after_rgb.jpg
    :alt: Picture after the RGB filter
