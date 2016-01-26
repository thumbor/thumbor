Responsive
==========

Description
-----------

This filter adds the possibility to create responsive images.
If this filter is active and a user requests a 320x240 image with a dpr of 2,
then a 640x480 image could be delivered.

The output size depends on other
things as well such as the source image resolution and the network quality.


Arguments
---------

display resolution value (dpr) (optional, number)
This value is the relationship between a CSS pixel and a physical pixel.
For desktop browsers this value is 1. For retina displays it is 2.

Valid values are from 0.5 to 4.


Example
-------

    ``/filters:dpr(2)/`` or ``/filters:dpr()/``


If no argument is given, then a dpr of 1 is assumed.
HTTP Client Hints can override the default value. If a value is passed in
as an argument, that value is used.