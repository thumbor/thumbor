Image storage
=============

thumbor uses image storages to perform less retrievals of images from
the sources, thus potentially saving expensive resources (such as
outbound network).

Pre-Packaged Storages
---------------------

thumbor comes with **filesystem**, **redis** and **mongodb** storages.
There's also a **nostorage** storage for debugging or benchmarking
purposes.

Filesystem Storage
~~~~~~~~~~~~~~~~~~

thumbor can store original images in the filesystem.

The file storage uses the **FILE\_STORAGE\_ROOT\_PATH** configuration
to save the images. It then joins the original image part of the URI to
create the proper path to store the image in the filesystem.

There's a **STORAGE\_EXPIRATION\_SECONDS** option that will determine
the time in seconds that a file is considered to be expired. When a file
is expired, thumbor will try to retrieve the file using the specified
:doc:`image_loader`.

To use the filesystem storage set the configuration option of
**STORAGE** to **'thumbor.storages.file\_storage'**.

Redis Storage
~~~~~~~~~~~~~

`Redis <http://redis.io/>`__ eliminates the risks of locks as well. In
order to use the redis storage set the configuration option of
**STORAGE** to **'thumbor.storages.redis\_storage'**.

You also need to configure the redis connection information using the
**REDIS\_STORAGE\_SERVER\_PORT**, **REDIS\_STORAGE\_SERVER\_HOST**
and **REDIS\_STORAGE\_SERVER\_DB**, like this:

.. code:: python

    REDIS_STORAGE_SERVER_HOST = 'localhost'
    REDIS_STORAGE_SERVER_PORT = 6379
    REDIS_STORAGE_SERVER_DB = 0

There's a **STORAGE\_EXPIRATION\_SECONDS** option that will determine
the time in seconds that a file is considered to be expired. When a file
is expired, thumbor will try to retrieve the file using the specified
:doc:`image_loader`.

MongoDB Storage
~~~~~~~~~~~~~~~

In order to use the `MongoDB <http://www.mongodb.org/>`__ storage set
the configuration option of **STORAGE** to
**'thumbor.storages.mongo\_storage'**.

You also need to configure the mongo connection information using the
**MONGO\_STORAGE\_SERVER\_PORT**, **MONGO\_STORAGE\_SERVER\_HOST**,
**MONGO\_STORAGE\_SERVER\_DB** and
**MONGO\_STORAGE\_SERVER\_COLLECTION**, like this:

.. code:: python

    MONGO_STORAGE_SERVER_HOST = 'localhost'
    MONGO_STORAGE_SERVER_PORT = 27017
    MONGO_STORAGE_SERVER_DB = 0
    MONGO_STORAGE_SERVER_COLLECTION = 'images'

There's a **STORAGE\_EXPIRATION\_SECONDS** option that will determine
the time in seconds that a file is considered to be expired. When a file
is expired, thumbor will try to retrieve the file using the specified
:doc:`image_loader`.

NoStorage Storage
~~~~~~~~~~~~~~~~~

This is a storage intended for debugging or benchmarking purposes. It
does not store any images and always returns None when thumbor asks for
an image.

In order to use this storage set the configuration option of
**STORAGE** to **'thumbor.storages.no\_storage'**.

MixedStorage Storage
~~~~~~~~~~~~~~~~~~~~

This is a storage intended for scenarios where you want to store the
original images files one way and the security key another (or detector
information).

A good example would be storing files in the filesystem, while storing
security keys in a database.

In order to use this storage set the configuration option of
**STORAGE** to **'thumbor.storages.mixed\_storage'**.

You must specify the ``MIXED_STORAGE_FILE_STORAGE``,
``MIXED_STORAGE_CRYPTO_STORAGE`` and ``MIXED_STORAGE_DETECTOR_STORAGE``
options to define the original images storage, the security key storage
and the detector results storage, respectively. Here's a sample
configuration:

.. code:: python

    MIXED_STORAGE_FILE_STORAGE = 'thumbor.storages.file_storage'
    MIXED_STORAGE_CRYPTO_STORAGE = 'thumbor.storages.redis_storage'
    MIXED_STORAGE_DETECTOR_STORAGE = 'thumbor.storages.redis_storage'

    FILE_STORAGE_ROOT_PATH = '/tmp/mypath'

    REDIS_STORAGE_SERVER_HOST = 'localhost'
    REDIS_STORAGE_SERVER_PORT = 6379
    REDIS_STORAGE_SERVER_DB = 0

As you can see, you still have to tell thumbor the specific
configurations for each storage you choose.

Custom Storages
---------------

If the built-in storages do not suit your needs, you can always
implement your own storage and use it in the **STORAGE**
configuration.

All you have to do is create a class called Storage that inherits from
BaseStorage in your module, as can be seen in 
`<https://github.com/thumbor/thumbor/blob/master/thumbor/storages/file_storage.py>`_.
