Welcome to Thumbor's documentation!
===================================

.. image:: https://raw.github.com/thumbor/thumbor/master/logo-thumbor.png

thumbor is a smart imaging service. It enables on-demand crop, resizing and flipping of images.

It also features a VERY smart detection of important points in the image for better cropping and resizing, using state-of-the-art face and feature detection algorithms (more on that in Detection Algorithms).

Using thumbor is very easy (after it is running). All you have to do is access it using an URL for an image, like this:

``http://<thumbor-server>/300x200/smart/s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg``

That URL would show an image of the big brother brasil participants in 300x200 using smart crop.

There are several other options to the image URL configuration. You can check them in the Usage page.

For more information check `thumbor's documentation <https://github.com/globocom/thumbor/wiki>`_.

Demo
====

You can see thumbor in action at http://thumborize.me/

.. toctree::
   :maxdepth: 2
   thumbor
   thumbor.engines
   thumbor.filters
   thumbor.loaders
   thumbor.optimizers
   thumbor.result_storages
   thumbor.storages

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

