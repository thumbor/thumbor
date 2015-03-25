Result Storage
==============

thumbor uses a result storage to improve the speed of responding
subsequent requests for the same image.

When a request for a given image with a set of parameters arrive,
thumbor processes the request and before returning it, asks for the
result storage to store it.

The next time the same request arrives, it will get it from the result
storage and return it, thus saving a lot of processing.

Pre-packaged result storages
----------------------------

thumbor comes pre-packaged with a filesystem result storage.

Filesystem
~~~~~~~~~~

The file system result storage, as the name implies, stores images in
the filesystem.

Images are stored in whatever path is specified in the
``RESULT_STORAGE_FILE_STORAGE_ROOT_PATH``, and consequently retrieved
from the same path.

By default, the file system result storage keeps images forever. You are
allowed to specify an expiration, though, using the
``RESULT_STORAGE_EXPIRATION_SECONDS`` configuration. Again, as the name
implies, it specifies the number of seconds with which files expire.

To use it you should set the ``RESULT_STORAGE`` configuration to
``'thumbor.result_storages.file_storage'``.

Creating a custom result storage
--------------------------------

In order to implement your own result storage, you have to implement a
few methods. A reference implementation can be found at the `File
Storage <https://github.com/thumbor/thumbor/blob/master/thumbor/result_storages/file_storage.py>`__.

The required methods are ``put``, ``get``, ``validate_path`` and
``normalize_path``.
