Image storage
=============

thumbor uses image storages to perform less retrievals of images from
the sources, thus potentially saving expensive resources (such as
outbound network).

Pre-Packaged Storages
---------------------

thumbor comes with **filesystem** and a **mixed** storage.
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

Compatibility Storage
~~~~~~~~~~~~~~~~~~~~~

The compatibility storage allows you to use legacy storages (that do not support AsyncIO)
in order to make it easier to transition to thumbor's Python 3 version.

To use it you should set the **STORAGE** configuration to
**'thumbor.compatibility.storage'**.

You also need to specify what's the legacy storage that the compatibility storage will use.
Just set the **COMPATIBILITY_LEGACY_STORAGE** configuration to the full name of the legacy
storage you want to use. i.e.: COMPATIBILITY_LEGACY_STORAGE = 'tc_aws.storages.s3_storage'
