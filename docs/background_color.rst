Filling
=======

Usage: background_color(color)

Description
-----------

The background_color filter sets the background layer set to specified color.
This is specifically useful when converting transparent images (PNG) to JPEG

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

.. image:: images/tom_before_background_color.png
    :alt: Original picture

`<http://localhost:8888/unsafe/fit-in/300x300/filters:background_color(blue)/https://github.com/thumbor/thumbor/wiki/tom_before_background_color.png>`_

.. image:: images/tom_background_color_blue.png
    :alt: Picture after the background_color(blue) filter

`<http://localhost:8888/unsafe/fit-in/300x300/filters:background_color(f00)/https://github.com/thumbor/thumbor/wiki/tom_before_background_color.png>`_

.. image:: images/tom_background_color_red.png
    :alt: Picture after the background_color(f00) filter

`<http://localhost:8888/unsafe/fit-in/300x300/filters:background_color(add8e6)/https://github.com/thumbor/thumbor/wiki/tom_before_background_color.png>`_

.. image:: images/tom_background_color_lightblue.png
    :alt: Picture after the background_color(add8e6)
