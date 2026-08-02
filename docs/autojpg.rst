AutoJPG
=======

Usage: `autojpg(enabled)`

Description
-----------

This filter overrides only the ``AUTO_PNG_TO_JPG`` fallback for the current
request. It does not enable or disable a ``jpg`` entry explicitly configured
in ``AUTO_IMAGE_FORMAT_PREFERENCE``.

Arguments
---------

- ``enabled`` - ``True`` enables PNG-to-JPEG fallback and ``False`` disables
  it for this request. The default is ``True``.

Example
-------

::

    http://localhost:8888/unsafe/300x300/filters:autojpg()/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg
