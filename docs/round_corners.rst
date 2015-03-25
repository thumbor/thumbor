Round corners
=============

Usage: round\_corner(a\|b,r,g,b)

Description
-----------

This filter adds rounded corners to the image using the specified color
as background.

Arguments
---------

a\|b - amount of pixels to use as radius. The argument b is not
required, but it specifies the second value for the ellipse used for the
radius.

Examples
--------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the round corners filter filter

`<http://thumbor-server/filters:round_corner(20,255,255,255)/some/image.jpg>`_
`<http://thumbor-server/filters:round_corner(20|40,0,0,0)/some/image.jpg>`_

.. image:: images/tom_after_round.jpg
    :alt: Picture after rounded corners
