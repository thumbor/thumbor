Focal
=====

Usage: focal(<left>x<top>:<right>x<bottom>)

Description
-----------

This filter adds a focal point, which is used in later transforms.

Arguments
---------

-  left, top, right, bottom: All mandatory arguments in the ``<left>x<top>:<right>x<bottom>`` format.

Example
-------

``http://localhost:8888/unsafe/400x100/filters:focal(146x156:279x208)/http://i.imgur.com/cldZwwc.jpg``

Before

.. image:: ../tests/fixtures/filters/source.jpg
    :alt: Picture after the RGB filter

After

.. image:: ../tests/fixtures/filters/focal.jpg
    :alt: Picture after the RGB filter