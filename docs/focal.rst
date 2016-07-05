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

``http://localhost:8888/unsafe/400x100/filters:focal(146x206:279x360)/https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Katherine_Maher.jpg/800px-Katherine_Maher.jpg``

Before

.. image:: ../tests/fixtures/filters/source.jpg
    :alt: Picture after the RGB filter

After

.. image:: ../tests/fixtures/filters/focal.jpg
    :alt: Picture after the RGB filter

Warning
-------

Unpredictable behavior may occur if using this filter with other functionality that set focal points, such as:

.. toctree::
   :maxdepth: 1

   extract_focal_points
   available_detectors
   metadata