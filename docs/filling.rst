Filling
=======

Usage: fill(color)

Description
-----------

This filter permit to return an image sized exactly as requested
wherever is its ratio by filling with chosen color the missing parts.
Usually used with "fit-in" or "adaptive-fit-in"

Arguments
---------

-  color - the color name (like in HTML) or hexadecimal rgb expression
   without the "#" character (see
   `<https://en.wikipedia.org/wiki/Web_colors>`_  for example). If color is
   "auto", a color will be smartly chosen (based on the image pixels) to
   be the filling color.

Example
-------

As original image is:

.. image:: images/tom_before_brightness.jpg
    :alt: Original picture

`<http://localhost:8888/unsafe/fit-in/300x300/filters:fill(blue)/https://github.com/thumbor/thumbor/wiki/tom_before_brightness.jpg>`_

.. image:: images/tom_fill_blue.jpg
    :alt: Picture after the fill(blue) filter

`<http://localhost:8888/unsafe/fit-in/300x300/filters:fill(f00)/https://github.com/thumbor/thumbor/wiki/tom_before_brightness.jpg>`_

.. image:: images/tom_fill_red.jpg
    :alt: Picture after the fill(f00) filter

`<http://localhost:8888/unsafe/fit-in/300x300/filters:fill(add8e6)/https://github.com/thumbor/thumbor/wiki/tom_before_brightness.jpg>`_

.. image:: images/tom_fill_lightblue.jpg
    :alt: Picture after the fill(add8e6)

`<http://localhost:8888/unsafe/fit-in/300x300/filters:fill(auto)/https://github.com/thumbor/thumbor/wiki/tom_before_brightness.jpg>`_

.. image:: images/tom_fill_auto.jpg
    :alt: Picture after the fill(auto) filter (since 3.7.1)
