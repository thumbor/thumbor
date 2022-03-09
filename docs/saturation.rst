Saturation
========

Usage: `saturation(amount)`

Description
-----------

This filter increases or decreases the image saturation.

Arguments
---------

- ``amount`` - :math:`-100` to :math:`100` - The amount (in %) to change the image saturation. Positive numbers increase saturation and negative numbers decrease saturation.

Example
-------

.. image:: images/tom_before_brightness.jpg
    :alt: Picture before the saturation filter

`<http://localhost:8888/unsafe/filters:saturation(40)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg>`_

.. image:: images/tom_after_positive_saturation.png
    :alt: Picture after positive saturation

`<http://localhost:8888/unsafe/filters:saturation(-40)/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg>`_

.. image:: images/tom_after_negative_saturation.png
    :alt: Picture after negative saturation
