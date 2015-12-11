Relase Notes
===========

** THIS PAGE IS HERE ONLY FOR HISTORIC PURPOSES, since we are now using `github releases page <https://github.com/thumbor/thumbor/releases>`__. **

Stable Release
--------------

4.1.0 - http://pypi.python.org/pypi/thumbor/4.1.0 - 02-Apr-2014

thumbor Releases
----------------

4.1.0 - http://pypi.python.org/pypi/thumbor/4.1.0 - 02-Apr-2014 - `diff <https://github.com/thumbor/thumbor/compare/4.0.4...4.1.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  New filter: `Extract Focal
   Points <https://github.com/thumbor/thumbor/wiki/Extract-Focal-Points>`__
-  Infrastructure for filters on different phases during the image
   processing lifecycle. Right now PHASE\_POST\_TRANSFORM and
   PHASE\_PRE\_LOAD are supported. All existing filters default to
   PHASE\_POST\_TRANSFORM

4.0.4 - http://pypi.python.org/pypi/thumbor/4.0.4 - 28-Mar-2014 - `diff <https://github.com/thumbor/thumbor/compare/4.0.3...4.0.4>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue with blur filter when used with more than 150 of radius
   (by @heynemann);
-  Fixed issue with format filter when used in conjunction with
   auto\_webp (by @cezarsa).

4.0.3 - http://pypi.python.org/pypi/thumbor/4.0.3 - 28-Mar-2014 - `diff <https://github.com/thumbor/thumbor/compare/4.0.2...4.0.3>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fix in all engines to return both image data and image mode together,
   instead of one or the other. If you implement your own engine, you
   need to create a new method called ``image_data_as_rgb`` that returns
   the image mode and the image bytes;
-  Thumbor Application class now has a ``get_handlers`` method that can
   be overwritten to specify new handlers.

4.0.2 - http://pypi.python.org/pypi/thumbor/4.0.2 - 18-Mar-2014 - `diff <https://github.com/thumbor/thumbor/compare/4.0.1...4.0.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue with WebP request path by `Frank
   Du <https://github.com/frankdu>`__;
-  Fixed issue with Upstart Script Log Level by `Matt
   Robenolt <https://github.com/mattrobenolt>`__;
-  Fixed issue with folder not existing before storing security details
   by `Cícero Verneck Corrêa <https://github.com/cicerocomp>`__;
-  Fixed `#272 <https://github.com/thumbor/thumbor/issues/272>`__ -
   Thumbor works properly with newer tornado.

4.0.1 - http://pypi.python.org/pypi/thumbor/4.0.1 - 18-Mar-2014 - `diff <https://github.com/thumbor/thumbor/compare/4.0.0...4.0.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue #289 - Now URLs with '~' should work properly.

4.0.0 - http://pypi.python.org/pypi/thumbor/4.0.0 - 12-Mar-2014 - `diff <https://github.com/thumbor/thumbor/compare/3.14.7...4.0.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WARNING
^^^^^^^

    This version contains breaking changes. Both GraphicsMagick and
    OpenCV engines were removed from the built-in imaging engines and
    can be found in the `thumbor
    organization <http://github.com/thumbor>`__ now. For more
    information on using each of them check the respective project
    documentation.

BREAKING Chances
^^^^^^^^^^^^^^^^

-  Removed thumbor.engines.opencv in favor of the new
   `opencv-engine <https://github.com/thumbor/opencv-engine>`__ project.
   That's where we'll maintain the OpenCV engine.
-  Removed thumbor.engines.graphicsmagick in favor of the new
   `graphicsmagick-engine <https://github.com/thumbor/graphicsmagick-engine>`__
   project. That's where we'll maintain the GraphicsMagick engine.

Fixed Issues
^^^^^^^^^^^^

-  Partitioning the FileStorage Result Storage into more folders by
   `Martin Sarsale <https://github.com/runa>`__;
-  Json File Error Handler by `Damien
   Hardy <https://github.com/dhardy92>`__;
-  Support binding socket to file descriptor instead of port by `John
   MacKenzie <https://github.com/198d>`__;
-  HEAD queries to thumbor's healthcheck returning 200 status code by
   `Damien Hardy <https://github.com/dhardy92>`__;
-  Fixed bug when parsing urls with filters of an original with filters
   by `Cezar Sá <https://github.com/cezarsa>`__;
-  Support different default quality for WebP images by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  Keep transparency when saving transparent gif by `Igor
   Sobreira <https://github.com/igorsobreira>`__;
-  Don't save PNG files as CMYK by `Igor
   Sobreira <https://github.com/igorsobreira>`__;
-  Upstart now uses ip var defined on ubuntu default file by `Paulo
   Sousa <https://github.com/morpheu>`__;
-  Fixed images cropped with width 1px and height 0px by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  Fixed #236 - IndexError: list index out of range by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  Fixed #235 - ValueError: Not a valid numbers of quantization tables.
   Should be between 2 and 4 by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  Fixed #228 - Confusing error when using OpenCV by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  New options to the fill filter by
   `prolificphotis <https://github.com/prolificphotis>`__;
-  Added FILL\_MERGES Configuration to specify whether the fill filter
   should merge the background by
   `prolificphotis <https://github.com/prolificphotis>`__;
-  Resolved quality config None in graphicsmagick engine by `Marcio
   Toshio Ide <https://github.com/marciotoshio>`__;
-  Preserving EXIF info when storing original images by `Cezar
   Sá <https://github.com/cezarsa>`__;
-  Resetting EXIF orientation after reorienting image by `Cezar
   Sá <https://github.com/cezarsa>`__;
-  Compatibility work for the fill filter across engines by `Cezar
   Sá <https://github.com/cezarsa>`__;
-  Pillow test\_requirement match setup.py by `Rob
   Olson <https://github.com/robolson>`__;
-  Fixed issues with graphicsmagick and gif images by `Bernardo
   Heynemann <https://github.com/heynemann>`__;
-  Convert to grayscale working in OpenCV Engine by `Pablo
   Aguiar <https://github.com/scorphus>`__.

New features
^^^^^^^^^^^^

-  New convolution filter by `Cezar Sá <https://github.com/cezarsa>`__;
-  New Gaussian Blur filter by `Cezar
   Sá <https://github.com/cezarsa>`__;

3.14.7 - http://pypi.python.org/pypi/thumbor/3.14.7 - 30-Oct-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.14.6...3.14.7>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Bumping tornado version to allow last update.

3.14.6 - http://pypi.python.org/pypi/thumbor/3.14.6 - 07-Oct-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.14.5...3.14.6>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Result storage disallows requesting files outside the root path.

3.14.5 - http://pypi.python.org/pypi/thumbor/3.14.5 - 25-Sep-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.14.4...3.14.5>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Not doing vary header or converting to WebP when image is an animated
   gif or already a WebP.

3.14.4 - http://pypi.python.org/pypi/thumbor/3.14.4 - 24-Sep-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.14.1...3.14.4>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Thumbor now includes a "Vary": "Accept" header to help cache servers
   to better understand that the image URL can vary by accept header.

3.14.1 - http://pypi.python.org/pypi/thumbor/3.14.1 - 02-Sep-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.13.3...3.14.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  A new filter has been introduced: max\_bytes. This filter allows
   users to specify the maximum number of bytes for the image. Thumbor
   will vary the quality of the image for JPEG and WebP images (png and
   gif images do not get affected by this filter).

3.13.3 - http://pypi.python.org/pypi/thumbor/3.13.3 - 31-Aug-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.13.2...3.13.3>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed `#193 <https://github.com/thumbor/thumbor/issues/193>`__. File
   storage now uses atomic storage of files, thus avoiding corruption of
   stored images.

3.13.2 - http://pypi.python.org/pypi/thumbor/3.13.2 - 31-Aug-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.13.1...3.13.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Merged `#202 <https://github.com/thumbor/thumbor/pull/202>`__. Proxy
   support added to default HTTP Loader.

3.13.1 - http://pypi.python.org/pypi/thumbor/3.13.1 - 31-Aug-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.13.0...3.13.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Merged `#197 <https://github.com/thumbor/thumbor/pull/197>`__.
   Healthcheck now replied to HEAD requests.

3.13.0 - http://pypi.python.org/pypi/thumbor/3.13.0 - 28-Aug-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.12.2...3.13.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#204 <https://github.com/thumbor/thumbor/issues/204>`__.
   Thumbor now allows users to specify that WebP should be automatically
   used whenever the request has the proper Accept header (image/webp).

3.12.2 - http://pypi.python.org/pypi/thumbor/3.12.2 - 12-Aug-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.12.1...3.12.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Added some extra logging to the finish request stage of the image
   handling.

3.12.1 - http://pypi.python.org/pypi/thumbor/3.12.1 - 18-Jul-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.12.0...3.12.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed leak of Redis connections when using queued detectors.

3.12.0 - http://pypi.python.org/pypi/thumbor/3.12.0 - 05-Jul-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.11.1...3.12.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed an issue with animated gifs (sigh);
-  Add detection support for WEBP format. Merge pull request
   `#194 <https://github.com/thumbor/thumbor/pull/194>`__ from
   dhardy92:feature\_Add\_WEBP\_Detection;
-  Support for the new release of Pillow (2.1.0) and works with Pillow
   master branch for now.

3.11.1 - http://pypi.python.org/pypi/thumbor/3.11.1 - 05-Jul-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.11.0...3.11.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Finished webp support;
-  Fixed a bug with webp support that would pass 'None' as format if no
   format specified;
-  Added a configuration ``PRESERVE_EXIF_INFO`` that when set to True
   will keep the exif metadata in images intact (including webp
   resulting images).

3.11.0 - http://pypi.python.org/pypi/thumbor/3.11.0 - 02-Jul-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.10.0...3.11.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Added 'format' filter. Now users can specify the output format using
   filters:format(webp) or filters:format(jpeg) and as follows. More
   information in the Filters page.
-  Partial webp support. Now webp images can be read as the source image
   and be used as the output image. Partial here means that the version
   we are using of pillow does not yet support ICC Profiles in WebP
   images. Only Chrome Canary does support ICC profiles right now, so
   this is not a real issue.
-  Improved openCV engine image resampling.
-  Proper integration with Pillow version 2.0.0.
-  Fixed HMAC signing if the key has unicode characters.

3.10.0 - http://pypi.python.org/pypi/thumbor/3.10.0 - 14-May-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.9.4...3.10.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#184 <https://github.com/thumbor/thumbor/issues/184>`__.
   Thumbor now reports expected errors as warning, instead of errors.
   This should allow users to use a logger level of ERROR to reduce the
   amount of I/O thumbor does for logging.
-  Fixes `#183 <https://github.com/thumbor/thumbor/issues/183>`__.
-  Fixes `#182 <https://github.com/thumbor/thumbor/issues/182>`__.
   There's two new configuration keys:
   ``HTTP_LOADER_DEFAULT_USER_AGENT`` and
   ``HTTP_LOADER_FORWARD_USER_AGENT``. These are meant to allow
   scenarios where the remote image server won't allow thumbor's user
   agent.
-  Fixes `#180 <https://github.com/thumbor/thumbor/issues/180>`__.
   Thumbor now features a grayscale filter. More information can be
   found in the Filters page.
-  Code reformatting to conform to PEP-8.

3.9.4 - http://pypi.python.org/pypi/thumbor/3.9.4 - 17-Apr-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.9.2...3.9.4>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Upgraded Pillow dependency to 2.0.0;
-  Normalized the Max Age header for images with smart detection errors
   around all detectors. Also included the ``IGNORE_SMART_ERRORS``
   setting that enables users to keep responding the image without smart
   cropping when smart detection throws exceptions. This setting is
   ``False`` by default and needs to be enabled explicitly (reverse
   compatibility);
-  Fixed an issue with sentry error handler;
-  **POSSIBLE BREAKING CHANGE**: We changed the way the http handler
   requests images. It now passes safer connection timeout, request
   timeout and follow redirects values to ``libcurl``. You can change
   those values in your configuration file using the
   ``HTTP_LOADER_CONNECT_TIMEOUT``, ``HTTP_LOADER_REQUEST_TIMEOUT``,
   ``HTTP_LOADER_FOLLOW_REDIRECTS`` and ``HTTP_LOADER_MAX_REDIRECTS``
   settings (more on those in the Configuration page). This change might
   break you if you have connect times greater than 5 seconds. This
   setting was previously configured to 20 seconds.

3.9.2 - http://pypi.python.org/pypi/thumbor/3.9.2 - 09-Apr-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.9.1...3.9.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Logging format can now be configured using ``THUMBOR_LOG_FORMAT`` and
   ``THUMBOR_LOG_DATE_FORMAT`` configuration variables. These are just
   passed through to python's ``format`` and ``datefmt`` arguments of
   the ``logging.basicConfig`` method.

3.9.1 - http://pypi.python.org/pypi/thumbor/3.9.1 - 09-Apr-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.9.0...3.9.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Makes error handling a little safer.

3.9.0 - http://pypi.python.org/pypi/thumbor/3.9.0 - 28-Mar-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.8.1...3.9.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#165 <https://github.com/thumbor/thumbor/issues/165>`__.
   Setting the ``ALLOW_ANIMATED_GIFS`` configuration to ``False`` will
   remove the experimental support for animated gifs.

3.8.1 - http://pypi.python.org/pypi/thumbor/3.8.1 - 27-Mar-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.7.1...3.8.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#175 <https://github.com/thumbor/thumbor/issues/175>`__.
   Thumbor now support custom error handling. This can be very useful
   for users that have a centralized error application (like
   `sentry <https://github.com/getsentry/sentry>`__).
-  `Sentry's <https://github.com/getsentry/sentry>`__ custom error
   handler comes built-in with thumbor.
-  Optimized fill filter, which is now implemented in C (by
   fabiomcosta).

3.7.1 - http://pypi.python.org/pypi/thumbor/3.7.1 - 06-Feb-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.7.0...3.7.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fix bug with quoting valid characters in URL (by cdemonchy);
-  Fix in debian packaging for Debian Squeeze (by dhardy92);
-  Fix in the mongo storage (by phpconnect);
-  Auto option for the fill filter (by fabiomcosta).

3.7.0 - http://pypi.python.org/pypi/thumbor/3.7.0 - 24-Jan-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.6.11...3.7.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Multi-Instance deb support. Merge pull request
   `#146 <https://github.com/thumbor/thumbor/pull/146>`__ from
   nhuray/master.

3.6.11 - http://pypi.python.org/pypi/thumbor/3.6.11 - 23-Jan-2013 - `diff <https://github.com/thumbor/thumbor/compare/3.6.10...3.6.11>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Implementing methods that were missing in the json engine;
-  Merge pull request
   `#143 <https://github.com/thumbor/thumbor/pull/143>`__ from
   nhuray/master;
-  Disable REST Upload by default;
-  Merge pull request
   `#142 <https://github.com/thumbor/thumbor/pull/142>`__ from
   morpheu/master;
-  Other detector options in thumbor.conf.

3.6.10 - http://pypi.python.org/pypi/thumbor/3.6.10 - 14-Dec-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.9...3.6.10>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#138 <https://github.com/thumbor/thumbor/issues/138>`__.
   Filters are not required for using thumbor.

3.6.9 - http://pypi.python.org/pypi/thumbor/3.6.9 - 12-Dec-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.8...3.6.9>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Improved error handling on http loader.

3.6.8 - http://pypi.python.org/pypi/thumbor/3.6.8 - 12-Dec-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.7...3.6.8>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#139 <https://github.com/thumbor/thumbor/issues/139>`__.
   Libmagic is not required anymore.
-  Improved image type detection.

3.6.7 - http://pypi.python.org/pypi/thumbor/3.6.7 - 24-Oct-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.6...3.6.7>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Pull request `#133 <https://github.com/thumbor/thumbor/pull/133>`__
   from gcirne.
-  Fixes `#132 <https://github.com/thumbor/thumbor/issues/132>`__.
   Thumbor has a rest API for uploading images from this version
   onwards. Documentation to follow.

3.6.6 - http://pypi.python.org/pypi/thumbor/3.6.6 - 24-Oct-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.4...3.6.6>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed some issues with thumbor-url.

3.6.4 - http://pypi.python.org/pypi/thumbor/3.6.4 - 24-Oct-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.3...3.6.4>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fix glasses detector - Pull request
   `#124 <https://github.com/thumbor/thumbor/pull/124>`__.
-  Pull request `#128 <https://github.com/thumbor/thumbor/pull/128>`__
   from wichert.
-  Update encrypted string to allow trim parameter;
-  Allow specifying trim option in URL composure and thumbor-url.

3.6.3 - http://pypi.python.org/pypi/thumbor/3.6.3 - 26-Sep-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.2...3.6.3>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#127 <https://github.com/thumbor/thumbor/issues/127>`__.

3.6.2 - http://pypi.python.org/pypi/thumbor/3.6.2 - 19-Sep-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.1...3.6.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#126 <https://github.com/thumbor/thumbor/issues/126>`__.

3.6.1 - http://pypi.python.org/pypi/thumbor/3.6.1 - 19-Sep-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.6.0...3.6.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#125 <https://github.com/thumbor/thumbor/issues/125>`__
   properly. Both libthumbor and ruby-thumbor verified now (Big Kudos to
   @robolson).

3.6.0 - http://pypi.python.org/pypi/thumbor/3.6.0 - 18-Sep-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.5.2...3.6.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed compilation under clang (Mac OS X Lion);
-  Included trim option to remove surrounding space in images `more
   info <https://github.com/thumbor/thumbor/wiki/Usage>`__;
-  Fixes `#125 <https://github.com/thumbor/thumbor/issues/125>`__.
-  Pull request `#124 <https://github.com/thumbor/thumbor/pull/124>`__.

3.5.2 - http://pypi.python.org/pypi/thumbor/3.5.2 - 14-Aug-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.5.1...3.5.2>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed support to custom apps;
-  Fixed issue with graphicsmagick manual crop method;
-  Added a custom-header to thumbor that specifies its name and version;
-  Changed filestorage to store uploaded files using a MD5 based hash
   algorithm similar to what git does.

3.5.1 - http://pypi.python.org/pypi/thumbor/3.5.1 - 03-Aug-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.5.0...3.5.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Added a new exception in the upload handler called
   ``BadRequestError`` as a way for storages to report to thumbor that
   some information that they required in the request was not provided.
   This way thumbor can return a ``400 BAD REQUEST`` response to the
   upload request.

3.5.0 - http://pypi.python.org/pypi/thumbor/3.5.0 - 03-Aug-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.4.1...3.5.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#113 <https://github.com/thumbor/thumbor/issues/113>`__ and
   `#114 <https://github.com/thumbor/thumbor/issues/113>`__, that were
   related.
-  Allow storage classes to retrieve request information in the
   ``resolve_original_path`` method.

**WARNING** - This release introduces a BREAKING CHANGE if you have your
own storage implemented. The method ``resolve_original_photo_path`` now
has a new signature. It used to be
``resolve_original_photo_path(filename)`` and now is
``resolve_original_photo_path(request, filename)``.

3.4.1 - http://pypi.python.org/pypi/thumbor/3.4.1 - 02-Aug-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.4.0...3.4.1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#115 <https://github.com/thumbor/thumbor/pull/115>`__.

3.4.0 - http://pypi.python.org/pypi/thumbor/3.4.0 - 01-Aug-2012 - `diff <https://github.com/thumbor/thumbor/compare/3.3.0...3.4.0>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#107 <https://github.com/thumbor/thumbor/pull/107>`__.
   9-Patch filter to support android 9-patch format-like images.
-  Fixes `#103 <https://github.com/thumbor/thumbor/issues/103>`__.
   Fixes handling special characters in the URLs.
-  A couple configuration keys renamed. For some time the old names will
   be kept compatible.
-  Introduction of https://github.com/globocom/derpconf, an abstraction
   for configuration files.

3.3.0 - http://pypi.python.org/pypi/thumbor/3.3.0 - 18-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#82 <https://github.com/thumbor/thumbor/issues/82>`__.
   There's a new command called 'thumbor-config' that will output
   thumbor's default configuration file.

-  Fixes `#94 <https://github.com/thumbor/thumbor/issues/94>`__.
   There's a new configuration called 'RESPECT\_ORIENTATION' that
   instructs thumbor to rotate images according to an EXIF orientation
   (if one can be found in the image headers).

3.2.0 - http://pypi.python.org/pypi/thumbor/3.2.0 - 18-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#103 <https://github.com/thumbor/thumbor/issues/103>`__.
   Tornado unquotes URL's passed to thumbor and that screws up some
   URLs.

3.1.1 - http://pypi.python.org/pypi/thumbor/3.1.1 - 17-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#102 <https://github.com/thumbor/thumbor/issues/102>`__.
   There was an additional issue with images with alpha channels (LA).

3.1.0 - http://pypi.python.org/pypi/thumbor/3.1.0 - 17-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue with gifsicle when optimizing GIF images.
-  Fixes `#102 <https://github.com/thumbor/thumbor/issues/102>`__. This
   was an issue with OpenCV and palette images.
-  Fixes with URL regexes.

3.0.2 - http://pypi.python.org/pypi/thumbor/3.0.2 - 9-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixing size and manual crop for animated gifs.

3.0.1 - http://pypi.python.org/pypi/thumbor/3.0.1 - 2-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some fixes: \* Fixed issue with filters in old style URLs. \* Supporting
meta in the thumbor-url console. \* Using storage crypto keys for hmac.

3.0.0 - http://pypi.python.org/pypi/thumbor/3.0.0 - 2-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**This release features a major change in the way URLs are handled**.
It's still backwards compatible, but the old style URLs are deprecated
and will go away in the next major. For more information read the
3.0.0 release changes.

-  Fixes `#98 <https://github.com/thumbor/thumbor/issues/98>`__.

2.8.2 - http://pypi.python.org/pypi/thumbor/2.8.2 - 9-Jul-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixing size and manual crop for animated gifs. (Backport from 3.0.2)

2.8.1 - http://pypi.python.org/pypi/thumbor/2.8.1 - 29-Jun-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes `#97 <https://github.com/thumbor/thumbor/issues/97>`__.
   Request parameters for the source image are now properly appended to
   the image URI.
-  Fixes `#96 <https://github.com/thumbor/thumbor/issues/96>`__.
   Experimental support for animated gifs. Most filters are working.
   Only for PIL engine. Other engines to come.

2.7.8 - http://pypi.python.org/pypi/thumbor/2.7.8 - 21-Jun-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes to the fill and watermark filters.

2.7.7 - http://pypi.python.org/pypi/thumbor/2.7.7 - 01-Jun-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  New filter to strip ICC heders
-  Issue with ORIG size and Max Height.
-  Encoding issues for Unicode named images.

2.7.4 - http://pypi.python.org/pypi/thumbor/2.7.4 - 30-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Support to "orig" style widths and heights.

2.7.3 - http://pypi.python.org/pypi/thumbor/2.7.3 - 23-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Issue #90\|https://github.com/thumbor/thumbor/issues/90 fixed.
   thumbor-url command now works properly.
-  Key file and adaptive cropping support in thumbor-url.

2.7.1 - http://pypi.python.org/pypi/thumbor/2.7.1 - 19-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Filter infrastructure refactored.

2.7.0 - http://pypi.python.org/pypi/thumbor/2.7.0 - 14-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Improvements in the upload feature.
-  Improvements in the C-Based filters.

2.6.12 - http://pypi.python.org/pypi/thumbor/2.6.12 - 05-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  New sharpen filter.

2.6.5 - http://pypi.python.org/pypi/thumbor/2.6.5 - 01-Mar-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue with fill filter.

2.6.4 - http://pypi.python.org/pypi/thumbor/2.6.4 - 23-Feb-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor fixes in the red eye and equalize filters.

2.6.3 - http://pypi.python.org/pypi/thumbor/2.6.3 - 21-Feb-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor fixes in the image uploading area.

2.6.2 - http://pypi.python.org/pypi/thumbor/2.6.2 - 20-Feb-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Ticket `#25 <https://github.com/thumbor/thumbor/issues/25>`__ in
   experimental status.
-  Ticket `#59 <https://github.com/thumbor/thumbor/issues/59>`__ done.

2.5.1 - http://pypi.python.org/pypi/thumbor/2.5.1 - 02-Feb-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Better handling errors in queued detectors;
-  Fallback to jpeg when we don't know the image type;
-  Increased test coverage.

2.5.0 - http://pypi.python.org/pypi/thumbor/2.5.0 - 30-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Refactored base detector not to depend on opencv anymore.

2.4.9 - http://pypi.python.org/pypi/thumbor/2.4.9 - 30-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Atomic file move for ResultStorage.

2.4.7 - http://pypi.python.org/pypi/thumbor/2.4.7 - 27-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Bug fixes.
-  Password support for redis storage.

2.4.6 - http://pypi.python.org/pypi/thumbor/2.4.6 - 24-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Bug fixes in Mongo and Redis Storages.

2.4.4 - http://pypi.python.org/pypi/thumbor/2.4.4 - 18-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor fixes in file descriptor management.

2.4.3 - http://pypi.python.org/pypi/thumbor/2.4.3 - 18-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  New setting that allows users to specify if unsafe images should be
   in result storage.

2.4.2 - http://pypi.python.org/pypi/thumbor/2.4.2 - 17-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor tweaks to result storage.

2.4.1 - http://pypi.python.org/pypi/thumbor/2.4.1 - 17-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Internal minor refactoring.

2.4.0 - http://pypi.python.org/pypi/thumbor/2.4.0 - 17-Jan-2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Major refactoring of thumbor internals. Should not affect thumbor
   usage.

2.3.0 - http://pypi.python.org/pypi/thumbor/2.3.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Features a RemoteCompleteDetector to perform both detections in one
   round-trip to remotecv.

2.2.0 - http://pypi.python.org/pypi/thumbor/2.2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Included support for remotecv.

2.1.0 - http://pypi.python.org/pypi/thumbor/2.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Updated tornado to release 2.1.1.

2.0.5 - http://pypi.python.org/pypi/thumbor/2.0.5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Improved PIL graphics engine to support different ICC profiles. It
   now keeps the existing ICC profile if there is one. This improves
   drastically the image quality. Very recommended update.

2.0.3 - http://pypi.python.org/pypi/thumbor/2.0.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes to native extensions used in filters.

2.0.2 - http://pypi.python.org/pypi/thumbor/2.0.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed issue with specifying the jsonp callback.

2.0.1 - http://pypi.python.org/pypi/thumbor/2.0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Debug mode.
-  Filter Support.
-  Brightness, Contrast, Noise, Quality, RGB, Round Corner and Watermark
   filters.
-  ImageMagick engine removed.
-  JSONP callback can now be passed as an argument.
-  Minor fixes.

1.2.1 - http://pypi.python.org/pypi/thumbor/1.2.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed minor issues with storing openCV results.

1.1.0 - http://pypi.python.org/pypi/thumbor/1.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed bug with smart cropping manual cropped images.

1.0.0 - http://pypi.python.org/pypi/thumbor/1.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed major bug with manual cropping.

0.9.6 - http://pypi.python.org/pypi/thumbor/0.9.6
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Crypto Handler refactored. Improved decrypting performance.

0.9.4 - http://pypi.python.org/pypi/thumbor/0.9.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixing the number of processes to one.

0.9.3 - http://pypi.python.org/pypi/thumbor/0.9.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes issue with mysql storage.

0.9.1 - http://pypi.python.org/pypi/thumbor/0.9.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixes issue with redis storage.

0.9.0 - http://pypi.python.org/pypi/thumbor/0.9.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Serious BUG Fix. OpenCV Detector data was being returned incorrectly.

0.8.2 - http://pypi.python.org/pypi/thumbor/0.8.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor Fixes.
-  Performance Fixes.

0.8.0 - http://pypi.python.org/pypi/thumbor/0.8.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #41 - Store in the storage the detection results for later
   usage. <https://github.com/thumbor/thumbor/issues#issue/41>`__

0.7.14 - http://pypi.python.org/pypi/thumbor/0.7.14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Minor Fixes.

0.7.11 - http://pypi.python.org/pypi/thumbor/0.7.11
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Loader and file storage fixed.

0.7.10 - http://pypi.python.org/pypi/thumbor/0.7.10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fit-in bug fixed.

0.7.9 - http://pypi.python.org/pypi/thumbor/0.7.9
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Some performance fixes and MixedStorage.

0.7.8 - http://pypi.python.org/pypi/thumbor/0.7.8
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #36 - Change Mongo Storage to use
   GridFS <https://github.com/thumbor/thumbor/issues#issue/36>`__

0.7.7 - http://pypi.python.org/pypi/thumbor/0.7.7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #29 - Create an OpenCV
   Engine <https://github.com/thumbor/thumbor/issues#issue/29>`__

0.7.6 - http://pypi.python.org/pypi/thumbor/0.7.6
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #35 - MySQL
   Storage <https://github.com/thumbor/thumbor/issues#issue/35>`__
-  `Ticket #31 - NoStorage Storage needs to be updated to include no
   crypto
   support <https://github.com/thumbor/thumbor/issues#issue/31>`__

0.7.5 - http://pypi.python.org/pypi/thumbor/0.7.5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #34 - Meta should have the option of returning as
   jsonp <https://github.com/thumbor/thumbor/issues#issue/34>`__
   (REOPENED)

0.7.4 - http://pypi.python.org/pypi/thumbor/0.7.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #34 - Meta should have the option of returning as
   jsonp <https://github.com/thumbor/thumbor/issues#issue/34>`__

0.7.2 - http://pypi.python.org/pypi/thumbor/0.7.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #32 - Allow unlimited dimensions of
   images <https://github.com/thumbor/thumbor/issues#issue/32>`__

0.7.0 - http://pypi.python.org/pypi/thumbor/0.7.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #30 - Allow users to use a fit-in
   flag <https://github.com/thumbor/thumbor/issues#issue/30>`__

0.6.5 - http://pypi.python.org/pypi/thumbor/0.6.5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #16 - NoStorage
   Storage <https://github.com/thumbor/thumbor/issues#issue/16>`__
-  `Ticket #24 - OpenCV File
   Issue <https://github.com/thumbor/thumbor/issues#issue/24>`__
-  `Ticket #26 - BUG: Redis Configuration does not
   work <https://github.com/thumbor/thumbor/issues#issue/26>`__
-  `Ticket #27 - BUG: Issue with
   cropping <https://github.com/thumbor/thumbor/issues#issue/27>`__

0.6.4 - http://pypi.python.org/pypi/thumbor/0.6.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #24 - OpenCV File
   Issue <https://github.com/thumbor/thumbor/issues#issue/7>`__

0.6.3 - http://pypi.python.org/pypi/thumbor/0.6.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Some refactoring and added App and Handler inheritance support.

0.6.2 - http://pypi.python.org/pypi/thumbor/0.6.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #7 - Validate for file size on the http
   loader <https://github.com/thumbor/thumbor/issues#issue/7>`__

0.6.1 - http://pypi.python.org/pypi/thumbor/0.6.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Switched encryption from Triple-Des to AES due to standardization
   between programming languages.

0.5.1 - http://pypi.python.org/pypi/thumbor/0.5.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fixed a bug with encrypting relative dimension images.

0.5.0 - http://pypi.python.org/pypi/thumbor/0.5.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #5 - Switch the unencrypted URL to be /unsafe and the
   encrypted to be the
   default <https://github.com/thumbor/thumbor/issues#issue/5>`__

0.4.1 - http://pypi.python.org/pypi/thumbor/0.4.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #4 - Bug in the encrypted URL generation and
   parsing <https://github.com/thumbor/thumbor/issues#issue/4>`__

0.4.0 - http://pypi.python.org/pypi/thumbor/0.4.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #2 - Command-line application to generate
   urls <https://github.com/thumbor/thumbor/issues#issue/2>`__

0.3.0 - http://pypi.python.org/pypi/thumbor/0.3.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Ticket #1 - URL Cryptography
   Support <https://github.com/thumbor/thumbor/issues#issue/1>`__
   (FIXED)
-  Internal logic refactored.

