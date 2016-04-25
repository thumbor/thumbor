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


Custom loaders
--------------

If thumbor image loaders do not meet your needs you can implement a new
image loader.

The structure of the module you should implement can be seen in the http
loader at
`<https://github.com/thumbor/thumbor/blob/master/thumbor/loaders/http_loader.py>`_.

The only required method to implement is the one that receives the
portion of the URI that has the original image path, named **load**.
This method also receives a callback and should call the callback with
the results of reading the image.

Another example can be seen in the filesystem loader at
`<https://github.com/thumbor/thumbor/blob/master/thumbor/loaders/file_loader.py>`_.

You can optionally implement a validate(URI) method that thumbor will
call to make sure that your loader can accept the user required URI.
