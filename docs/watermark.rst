Watermark
=========

Usage: watermark(imageUrl, x, y, alpha)

Description
-----------

This filter adds a watermark to the image. It can be positioned inside the image
with the alpha channel specified.

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
   If the value is a positive or negative number followed by a 'p' (ex. 20p) it will calculate the value
   from the image width as percentage
-  y - Vertical position that the watermark will be in. Positive numbers
   indicate position from the top and negative numbers indicate position
   from the bottom.
   If the value is 'center' (without the single quotes), the watermark will be centered vertically.
   If the value is 'repeat' (without the single quotes), the watermark will be repeated vertically
   If the value is a positive or negative number followed by a 'p' (ex. 20p) it will calculate the value
   from the image height as percentage
-  alpha - Watermark image transparency. Should be a number between 0
   (fully opaque) and 100 (fully transparent).

Example
-------

|original|

`<http://thumbor-server/filters:watermark(http://my.site.com/img.png,-10,-10,50)/some/image.jpg>`_

|watermark|

`<http://thumbor-server/filters:watermark(http://my.site.com/img.png,10p,-20p,50)/some/image.jpg>`_

|watermark_relative|

.. |original| image:: images/tom_before_brightness.jpg
    :alt: Picture before the watermark filter

.. |watermark| image:: images/tom_after_watermark.jpg
    :alt: Picture after the watermark filter

.. |watermark_relative| image:: images/tom_watermark_relative.jpg
    :alt: Picture explaining watermark relative placement feature
