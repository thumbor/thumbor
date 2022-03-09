Sharpen
=======

Usage: `sharpen(sharpen\_amount,sharpen\_radius,luminance\_only)`

Description
-----------

This filter enhances apparent sharpness of the image. It's heavily based
on Marco Rossini's excellent Wavelet sharpen GIMP plugin. Check
`<http://registry.gimp.org/node/9836>`_ for details about how it work.

Arguments
---------

-  ``sharpen_amount`` - Sharpen amount. Typical values are between :math:`0.0` and
   :math:`10.0`.
-  ``sharpen_radius`` - Sharpen radius. Typical values are between :math:`0.0` and
   :math:`2.0`.
-  ``luminance_only`` - Sharpen only luminance channel. Values can be
   ``true`` or ``false``.

Example 1
---------

.. image:: images/man_before_sharpen.png
    :alt: Picture before the sharpen filter

::

    http://localhost:8888/unsafe/filters:sharpen(2,1.0,true)/http://videoprocessing.ucsd.edu/~stanleychan/research/pix/Blurred_foreman_0005.png

.. image:: images/man_after_sharpen.png
    :alt: Picture after the sharpen filter

Example 2
---------

.. image:: images/eagle_before_sharpen.jpg
    :alt: Picture before the sharpen filter

::

    http://localhost:8888/unsafe/filters:sharpen(1.5,0.5,true)/http://images.cambridgeincolour.com/tutorials/sharpening_eagle2-original.jpg

.. image:: images/eagle_after_sharpen.jpg
    :alt: Picture after the sharpen filter
