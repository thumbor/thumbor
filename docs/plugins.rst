Plugins
=======

With its pluggable architecture, thumbor provides extension points for a
myriad of plug-in: storages, loaders, detectors, filters.

If your plug-in is not listed here, please create an issue with the
details and we'll add it here.

Storages
--------

`thumbor\_aws <https://github.com/thumbor-community/aws>`__ (by `Thumbor Community <https://github.com/thumbor-community>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Thumbor <https://github.com/thumbor/thumbor/wiki>`__ is a smart
imaging service. It enables on-demand crop, resizing and flipping of
images.

`AWS <https://aws.amazon.com/>`__ is a cloud service, providing - among other things - storage capabilities.

This module provides support for AWS S3 interconnection, as a loader, a storage and/or a result storage.

-  *URL:* https://github.com/thumbor-community/aws
-  *Installing:* ``pip install tc_aws``

To get exhaustive details about configuration options & setting it up, go to the `documentation of the plugin <https://github.com/thumbor-community>`__.

`thumbor\_hbase <https://github.com/dhardy92/thumbor_hbase>`__ (by `Damien Hardy <https://github.com/dhardy92>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Thumbor <https://github.com/thumbor/thumbor/wiki>`__ is a smart
imaging service. It enables on-demand crop, resizing and flipping of
images.

`Hbase <https://hbase.apache.org/>`__ is a column oriented database from
the hadoop ecosystem.

This module provide support for Hadoop Hbase as large auto replicant
key/value backend storage for images in Thumbor.

-  *URL:* https://github.com/dhardy92/thumbor\_hbase
-  *Installing:* ``pip install thumbor_hbase``

Using it is simple, just change your configuration in thumbor.conf:

::

    HBASE_STORAGE_SERVER_HOST = "localhost"
    HBASE_STORAGE_SERVER_PORT = 9000
    HBASE_STORAGE_TABLE = "storage-table"
    HBASE_STORAGE_FAMILY = "storage-family"

If you want to use thumbor\_hbase for loading original images, change
your thumbor.conf to read:

::

    LOADER = "thumbor_hbase.loader"

If you want to use thumbor\_hbase for storage of original images, change
your thumbor.conf to read:

::

    STORAGE = "thumbor_hbase.storage"

`thumbor\_mongodb <https://github.com/dhardy92/thumbor_mongodb>`__ (by `Damien Hardy <https://github.com/dhardy92>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Thumbor <https://github.com/thumbor/thumbor/wiki>`__ is a smart
imaging service. It enables on-demand crop, resizing and flipping of
images.

`MongoDB <http://www.mongodb.org/>`__ is a document oriented NoSQL
database.

This plugin for Thumbor is a loader that can reach images from a mongodb
collection based on its Object(\_id).

-  *URL:* https://github.com/dhardy92/thumbor\_mongodb
-  *Installing:* ``pip install thumbor_mongodb``

Using it is simple, just change your configuration in thumbor.conf:

::

    LOADER = 'thumbor_mongodb.loader'
    MONGO_LOADER_CNX_STRING = 'mongodb://mongodbserver01,mongodbserver02:27017'
    MONGO_LOADER_SERVER_DB = 'thumbor'
    MONGO_LOADER_SERVER_COLLECTION = 'images'
    MONGO_LOADER_DOC_FIELD = 'content'

`thumbor\_riak <https://github.com/dhardy92/thumbor_riak>`__ (by `Damien Hardy <https://github.com/dhardy92>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Riak <http://basho.com/riak/>`__ is a distributed document oriented
database implementing the consistent hashing algorythm from the Dynanmo
publication by Amazon.

This module provide support for Riak as a large auto replicant key/value
backend storage for images in Thumbor.

-  *URL:* https://github.com/dhardy92/thumbor\_riak
-  *Installing:* ``pip install thumbor_riak`` (require thumbor)

Using it is simple, just change your configuration in thumbor.conf:

::

    # Use riak for storage.
    STORAGE = 'thumbor_riak.storage'

    # Put the url for your riak install here
    RIAK_STORAGE_BASEURL = "http://my-riak-install-base-url"

`thumbor\_rackspace <https://github.com/CodingNinja/thumbor_rackspace>`__ (by `David Mann <https://github.com/CodingNinja>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This plugin allows users to store objects in the Rackspace cloud for
result storage.

-  *URL:* https://github.com/CodingNinja/thumbor\_rackspace
-  *Installing:* ``pip install thumbor_rackspace``

Using it is simple, just change your configuration in thumbor.conf:

::

    # Use rackspace for result storage.
    # For more info on result storage: https://github.com/thumbor/thumbor/wiki/Result-storage
    RESULT_STORAGE = 'thumbor_rackspace.result_storages.cloudfile_storage'

    # Pyrax Rackspace configuration file location
    RACKSPACE_PYRAX_CFG = /var/thumbor/.pyrax.cfg

    # Result Storage options
    RACKSPACE_RESULT_STORAGE_EXPIRES = True # Set TTL on cloudfile objects
    RACKSPACE_RESULT_STORAGES_CONTAINER = "cloudfile-container-name"
    RACKSPACE_RESULT_STORAGES_CONTAINER_ROOT = "/"

`thumbor\_ceph <https://github.com/ksperis/thumbor_ceph>`__ (by `Laurent Barbe <https://github.com/ksperis>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Ceph <https://ceph.com/>`__ a distributed object store designed to
provide excellent performance, reliability and scalability.

This module provide support for Ceph RADOS as backend storage for
images.

-  *URL:* https://github.com/ksperis/thumbor\_ceph
-  *Installing:*
   ``apt-get install python-ceph && pip install thumbor_ceph``

Configuration in thumbor.conf:

::

    ################################# File Storage #################################
    STORAGE = 'thumbor_ceph.storages.ceph_storage'
    CEPH_STORAGE_POOL = 'thumbor'

    #################################### Upload ####################################
    UPLOAD_PHOTO_STORAGE = 'thumbor_ceph.storages.ceph_storage'

    ################################ Result Storage ################################
    RESULT_STORAGE = 'thumbor_ceph.result_storages.ceph_storage'
    CEPH_RESULT_STORAGE_POOL = 'thumbor'

For monitors and keys, the values ​​used are those defined in the
configuration file ceph.conf.

Extensions
----------

`thumbor\shortener <https://github.com/thumbor-community/shortener>`__ (by `Thumbor Community <https://github.com/thumbor-community>`__)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Thumbor <https://github.com/thumbor/thumbor/wiki>`__ is a smart
imaging service. It enables on-demand crop, resizing and flipping of
images.

This module provides URL shortening capabilities for Thumbor. It will create an API that can shorten a thumbor URL, and then routing capabilities to reroute the shortened URL to the correct image.

The shortened URL / real URL mapping is stored within redis.

-  *URL:* https://github.com/thumbor-community/shortener
-  *Installing:* ``pip install tc_shortener``

To get exhaustive details about configuration options & setting it up, go to the `documentation of the plugin <http://thumbor-shortener.readthedocs.io/en/latest/>`__.
