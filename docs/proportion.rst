Proportion
====

Usage: proportion(percentage)

Description
-----------

This filter applies porportion to height and width passed for cropping.

Arguments
---------

-  percentage - The percentage of the proportion. For exemple in this url http://localhost:8888/unsafe/300x300/filters:proportion(0.5)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png The Thumbor would crop this image with 150px of width and 150px of height, 50% of original cropping arguments.

Example
-------

``http://localhost:8888/unsafe/300x300/filters:proportion(0.5)/https://github.com/thumbor/thumbor/wiki/dice_transparent_background.png``