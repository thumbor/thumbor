Getting Started
===============

If you just want to give thumbor a try, it is pretty easy to get
started. **It won't take more than a minute.**

Just install it with ``pip install thumbor`` and start the process with
``thumbor`` in a console. That's all you need to start transforming images.

The image we'll be using in most of our examples is a Creative Commons licensed image by `Snapwire <https://www.pexels.com/@snapwire>`_::

   https://github.com/thumbor/thumbor/raw/master/example.jpg

.. image:: https://github.com/thumbor/thumbor/raw/master/example.jpg

If you want to use a different image, go ahead. Any image will work for the remainder of the docs.

.. note::
   Thumbor only understands properly encoded URIs. In order to use the URI above
   (or any other for that matter), we first need to encode it. This can be easily
   achieved by going to any modern browser's developer console and typing::

      window.encodeURIComponent(
        "https://github.com/thumbor/thumbor/raw/master/example.jpg"
      )

   And the output will be::

      https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

   That's the URL we'll be using in our examples!


Problems installing thumbor locally
-----------------------------------

No worries! If you have a docker host accessible, just run::

   $ docker run -p 8888:80 ghcr.io/minimalcompact/thumbor:latest

After downloading the image and running it, thumbor will be accessible at ``http://localhost:8888/``.

For more details check the `MinimalCompact thumbor docker image <https://github.com/MinimalCompact/thumbor>`_.

Changing its size
-----------------

Go to your browser and enter in the url::

   http://localhost:8888/unsafe/300x200/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

You should see the image with :math:`300px` of width and :math:`200px` of
height. Just play with it in the url to see the image change.

If you just want it to be proportional to the width, enter a height of
0, like::

   http://localhost:8888/unsafe/300x0/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

Flipping the image
------------------

How about seeing it backwards? Or upside down?

Go to your browser and enter in the url::

   http://localhost:8888/unsafe/-0x-0/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

You should see the waterfall backwards and upside down.

Filters
-------

What if I want to change contrast or brightness?

Go to your browser and enter in the url::

   http://localhost:8888/unsafe/filters:brightness(10):contrast(30)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

There are many more filters to explore. Check the :doc:`filters` page for more details.

What now?
---------

Ok, now that you know how amazing thumbor is, there's actually A LOT
more to it. Go check the rest of the docs to learn how to get even more
from your new imaging server.
