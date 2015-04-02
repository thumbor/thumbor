Creating my own Storage
=======================

In order to create your own original photo storage, all you have to do
is implement a class called ``Storage`` that inherits from
``thumbor.storages.BaseStorage`` and has three simple methods: ``put``,
``exists`` and ``remove``.

``put`` is the method that actually stores the image somewhere. It could
send the picture to a remote storage like Amazon's S3 or it could just
save the picture to the local filesystem. This method should have a
signature of ``put(path, bytes)`` and it should return the file path
(for future reference).

``exists`` should return if the file in the given path already exists.
This method should have a signature of ``exists(path)`` and it should
return a boolean stating if the file exists.

``remove`` should just remove the file in the given path. This method
*must* be idempotent, meaning that if the file has already been removed
(or does not exist for that matter) it shouldn't do anything on
subsequent calls. This method should have a signature of
``remove(path)`` and does not need to return anything.

After your class has been created (and hopefully tested, lol), you just
need to modify the ``ORIGINAL_PHOTO_STORAGE`` configuration option in
your thumbor.conf file to the module where you implemented your
``Storage`` class. Please note that thumbor must be able to import this
module, so it should be somewhere in the PYTHONPATH you started thumbor
with.
