AutoJPG
=======

Usage: `autojpg(enabled)`

Description
-----------

This filter overrides ``AUTO_PNG_TO_JPG`` config variable.

Arguments
---------

-  enabled - Passing ``True``, which is the default value, you will override the ``AUTO_PNG_TO_JPG`` config variable and False to keep the default behavior of thus config.

Example
-------

::

    http://localhost:8888/unsafe/300x300/filters:autojpg()/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
