Cover
=====

Usage: `cover()`

Description
-----------

This filter is used in GIFs to extract their first frame as the image to be used as cover.

.. note::

    This filter will only function when ``USE_GIFSICLE_ENGINE`` are set to ``True`` in ``thumbor.conf``:

.. code:: python

    USE_GIFSICLE_ENGINE = True

Arguments
---------

No arguments.

Example
-------

.. image:: images/animated.gif
    :alt: Gif before cover filter

::

    `http://localhost:8888/unsafe/filters:cover()/http://server.my/animated_static.gif`

.. image:: images/animated_static.gif
    :alt: Gif after cover filter
