Filling
=======

Usage: `fill(color[,fill_transparent])`

Description
-----------

This filter permit to return an image sized exactly as requested
wherever is its ratio by filling with chosen color the missing parts.
Usually used with "fit-in" or "adaptive-fit-in"

Arguments
---------

-  color - the color name (like in HTML) or hexadecimal RGB expression
   without the "#" character (see
   `<https://en.wikipedia.org/wiki/Web_colors>`_ for example).

   If color is "transparent" and the image format, supports transparency the
   filling color is transparent [1]_.

   If color is "auto", a color is smartly chosen (based on the image pixels)
   as the filling color.

   If color is "blur", the missing parts are filled with blurred original image.

-  fill_transparent - a boolean to specify whether transparent areas of the
   image should be filled or not. Accepted values are either `true`, `false`,
   `1` or `0`. This argument is optional and the default value is `false`.

Example #1
----------

The original image is:

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

`<http://localhost:8888/unsafe/fit-in/300x300/filters:fill(blur)/https://github.com/thumbor/thumbor/wiki/tom_before_brightness.jpg>`_

.. image:: images/tom_fill_blur.jpg
    :alt: Picture after the fill(blur) filter (since 6.7.1)

Example #2
----------

The original image is:

.. image:: images/dice_transparent_background.png
    :alt: Original picture

`<http://localhost:8888/unsafe/fit-in/300x225/filters:fill(blue,1)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_

.. image:: images/dice_blue_background.png
    :alt: Picture after the fill(blue) filter

`<http://localhost:8888/unsafe/fit-in/300x225/filters:fill(f00,true)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_

.. image:: images/dice_red_background.png
    :alt: Picture after the fill(f00) filter

`<http://localhost:8888/unsafe/fit-in/300x225/filters:fill(add8e6,1)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_

.. image:: images/dice_lightblue_background.png
    :alt: Picture after the fill(add8e6)

`<http://localhost:8888/unsafe/fit-in/300x225/filters:fill(auto,true)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_

.. image:: images/dice_auto_background.png
    :alt: Picture after the fill(auto) filter (since 3.7.1)

`<http://localhost:8888/unsafe/fit-in/300x225/filters:fill(blur,true)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png>`_

.. image:: images/dice_blur_background.png
    :alt: Picture after the fill(blur) filter (since 6.7.1)

.. [1] OpenCV Engine does not support transparent filling
