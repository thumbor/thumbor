Convolution
===========

Usage: `convolution(matrix\_items, number\_of\_columns, should\_normalize)`

Description
-----------

This filter runs a convolution matrix (or kernel) on the image. See
`Kernel (image
processing) <http://en.wikipedia.org/wiki/Kernel_(image_processing)>`__
for details on the process. Edge pixels are always extended outside the
image area.

Arguments
---------

-  ``matrix_items`` - Semicolon separated matrix items.
-  ``number_of_columns`` - Number of columns in the matrix.
-  ``should_normalize`` - Whether or not we should divide each matrix item by the sum of all items.

Example
-------

.. image:: images/before_convolution.png
    :alt: Picture before the convolution filter

Normalized Matrix:

::

    1 2 1
    2 4 2
    2 1 2

::

    http://localhost:8888/unsafe/filters:convolution(1;2;1;2;4;2;1;2;1,3,true)/http://upload.wikimedia.org/wikipedia/commons/5/50/Vd-Orig.png

.. image:: images/after_convolution1.png
    :alt: Picture after the convolution filter

Matrix:

::

    -1 -1 -1
    -1  8 -1
    -1 -1 -1

::

    http://localhost:8888/unsafe/filters:convolution(-1;-1;-1;-1;8;-1;-1;-1;-1,3,false)/http://upload.wikimedia.org/wikipedia/commons/5/50/Vd-Orig.png

.. image:: images/after_convolution2.png
    :alt: Picture after the convolution filter
