Strip EXIF
==========

Usage: `strip\_exif()`

Description
-----------

This filter removes any Exif information in the resulting image. To keep the copyright information you have to set the configuration ``PRESERVE_EXIF_COPYRIGHT_INFO = True``.

This is useful if you have set the configuration ``PRESERVE_EXIF_INFO = True`` but still wish to overwrite this behavior in some cases
(e.g. for image icons)


Arguments
---------

No arguments

Example
-------

::

    http://localhost:8888/unsafe/filters:strip\_exif()/http://www.arte.tv/static-epgapi/057460-011-A.jpg
