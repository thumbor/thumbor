Watermark
=========

Usage: watermark(imageUrl,x,y,alpha)

Description
-----------

This filter adds a watermark to the image.

Arguments
---------

-  imageUrl - Watermark image URL. It is very important to understand
   that the same image loader that Thumbor uses will be used here. If
   this URL contains parentheses they MUST be url encoded, since these
   are the characters Thumbor uses as delimiters for filter parameters.
-  x - Horizontal position that the watermark will be in. Positive
   numbers indicate position from the left and negative numbers indicate
   position from the right.
   If the value is 'center' (without the single quotes), the watermark will be centered horizontally.
   If the value is 'repeat' (without the single quotes), the watermark will be repeated horizontally.
-  y - Vertical position that the watermark will be in. Positive numbers
   indicate position from the top and negative numbers indicate position
   from the bottom.
   If the value is 'center' (without the single quotes), the watermark will be centered vertically.
   If the value is 'repeat' (without the single quotes), the watermark will be repeated vertically
-  alpha - Watermark image transparency. Should be a number between 0
   (fully opaque) and 100 (fully transparent).

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the watermark filter

`<http://thumbor-server/filters:watermark(http://my.site.com/img.png,-10,-10,50)/some/image.jpg>`_

.. image:: images/tom_after_watermark.jpg
    :alt: Picture after the watermark filter
