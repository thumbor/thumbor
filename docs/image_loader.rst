Image loader
============

Pre-packaged loaders
--------------------

thumbor comes pre-packaged with http and filesystem loaders.

Http loader
~~~~~~~~~~~

The http loader gets the original image portion of the URI and performs
an HTTP GET to it. It then returns the image's string representation.

The http loader uses the **ALLOWED\_SOURCES** configuration to
determine whether or not an image is from a trusted source and can thus
be loaded.

You can specify the maximum size of the source image to be loaded. The
http loader first gets the image size (without loading its contents),
checks against your specified size and returns 404 if the source image
size is larger than the max size. The max size option is
**MAX\_SOURCE\_SIZE** and the default is no maximum size.

To use it you should set the **LOADER** configuration to
**'thumbor.loaders.http\_loader'**.

Https loader
~~~~~~~~~~~~

The https loader works the same way as the http loader, except that it
defaults to https instead of http.

To use it you should set the **LOADER** configuration to
**'thumbor.loaders.https\_loader'**.

Strict https loader
~~~~~~~~~~~~~~~~~~~

The strict https loader works the same way as the http loader, except
that it only allows to load images over https.

To use it you should set the **LOADER** configuration to
**'thumbor.loaders.strict\_https\_loader'**.

File loader
~~~~~~~~~~~

The file loader gets the original image portion of the URI and retrieves
the file from the file system from a known path specified by the
**FILE\_LOADER\_ROOT\_PATH** configuration.

It joins the specified path with the configured root path and reads the
image file if it exists.

To use it you should set the **LOADER** configuration to
**'thumbor.loaders.file\_loader'**.

File loader with http loader fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some environments you need both kinds of file loading. For this use case
you can use as loader with built-in fallback.

This loader will try to load images from local file storage. In case
of an error the loader retry to load image with http\_loader. If both attempts failed
you'll get an error.

To use it you should set the **LOADER** configuration to
**'thumbor.loaders.file\_loader\_http\_fallback'**.

Compatibility Loader
~~~~~~~~~~~~~~~~~~~~

The compatibility loader allows you to use legacy loaders (that do not support AsyncIO)
in order to make it easier to transition to thumbor's Python 3 version.

To use it you should set the **LOADER** configuration to
**'thumbor.compatibility.loader'**.

You also need to specify what's the legacy loader that the compatibility loader will use.
Just set the **COMPATIBILITY_LEGACY_LOADER** configuration to the full name of the legacy
loader you want to use. i.e.: COMPATIBILITY_LEGACY_LOADER = 'tc_aws.loaders.s3_loader'
