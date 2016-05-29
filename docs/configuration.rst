Configuration
=============

thumbor's configuration file is just a regular python script that
thumbor loads.

In order to get a commented configuration file, just run:

::

    thumbor-config > ./thumbor.conf

Extensibility Section
---------------------

LOADER
~~~~~~

The loader is responsible for retrieving the source image that thumbor
will work with. This configuration defines the module that thumbor will
use for it. **This must be a full namespace module (a.k.a. python has to
be able to **import** it).**

i.e.: thumbor.loaders.http\_loader

STORAGE
~~~~~~~

The storage is responsible for storing the source image bytes and
related metadata (face-detection, encryption and such) so that we don't
keep loading it every time. **This must be a full namespace module
(a.k.a. python has to be able to **import** it).**

i.e.: thumbor.storages.file\_storage

MIXED\_STORAGE\_FILE\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(thumbor.storages.mixed\_storage), this is where you specify the storage
that will be used to store images. **This must be a full namespace
module (a.k.a. python has to be able to **import** it).**

i.e.: thumbor.storages.file\_storage

MIXED\_STORAGE\_CRYPTO\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(thumbor.storages.mixed\_storage), this is where you specify the storage
that will be used to store cryptography information. **This must be a
full namespace module (a.k.a. python has to be able to **import** it).**

i.e.: thumbor.storages.redis\_storage

MIXED\_STORAGE\_DETECTOR\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(thumbor.storages.mixed\_storage), this is where you specify the storage
that will be used to store facial and feature detection results. **This
must be a full namespace module (a.k.a. python has to be able to
**import** it).**

i.e.: thumbor.storages.mongo\_storage

ENGINE
~~~~~~

The engine is responsible for transforming the image. **This must be a
full namespace module (a.k.a. python has to be able to **import** it).**

Thumbor ships with three imaging engines:

-  thumbor.engines.pil
-  thumbor.engines.opencv
-  thumbor.engines.graphicsmagick
-

   .. raw:: html

      <del>

   thumbor.engines.imagemagick

   .. raw:: html

      </del>

   (This engine isn't supported anymore, check
   `#52 <https://github.com/thumbor/thumbor/issues/52>`__)

RESULT\_STORAGE
~~~~~~~~~~~~~~~

The result storage is responsible for storing the resulting image with
the specified parameters (think of it as a cache), so that we don't keep
processing it every time a request comes in. **This must be a full
namespace module (a.k.a. python has to be able to **import** it).**

i.e.: thumbor.result\_storages.file\_storage

URL\_SIGNER
~~~~~~~~~~

The url signer is responsible for validation and signing of requests to prevent url tampering,
which could lead to denial of service (example: filling the result_storage by specifying a different size).
**This must be a full namespace module (a.k.a. python has to be able to **import** it).**

i.e.: libthumbor.url\_signers.base64\_hmac\_sha1

Filters Section
---------------

In order to specify the filters that thumbor will use, you need a
configuration key called FILTERS. This is a regular python list with the
full names (names that python can import) of the filter modules you want
to use.

An example:

.. code:: python

    FILTERS = [
        'thumbor.filters.brightness',
        'thumbor.filters.contrast',
        'thumbor.filters.rgb',
        'thumbor.filters.round_corner',
        'thumbor.filters.quality',
        'thumbor.filters.noise',
        'thumbor.filters.watermark',
    ]

Metadata Section
----------------

META\_CALLBACK\_NAME
~~~~~~~~~~~~~~~~~~~~

If you want thumbor to use JSONP for image metadata instead of using
JSON, just set this variable to the callback name you want.

i.e.: "thumbor\_callback"

Face and Feature Detection Section
----------------------------------

DETECTORS
~~~~~~~~~

This options specifies the detectors that should run the image to check
for focal points.

i.e.: ["thumbor.detectors.face\_detector",
"thumbor.detectors.feature\_detector"]

FACE\_DETECTOR\_CASCADE\_FILE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the cascade (XML) file path to train openCV to
find faces.

i.e.: haarcascade\_frontalface\_alt.xml

Imaging Section
---------------

ALLOWED\_SOURCES
~~~~~~~~~~~~~~~~

This configuration defines the source of the images that thumbor will
load. This is only used in the HttpLoader (check the LOADER
configuration above).

i.e.: ALLOWED\_SOURCES=['http://s.glbimg.com']

Another example with wildcards:

ALLOWED\_SOURCES = ['.+.globo.com', '.+.glbimg.com']

This is to get any images that are in *.globo.com or *.glbimg.com and it
will fail with any other domains.

MAX\_WIDTH and MAX\_HEIGHT
~~~~~~~~~~~~~~~~~~~~~~~~~~

These define the box that the resulting image for thumbor must fit-in.
This means that no image that thumbor generates will have a width larger
than MAX\_WIDTH or height larger than MAX\_HEIGHT.

i.e.:

::

    MAX_WIDTH = 1200
    MAX_HEIGHT = 800

MIN\_WIDTH and MIN\_HEIGHT
~~~~~~~~~~~~~~~~~~~~~~~~~~

These define the box that the resulting image for thumbor must fit-in.
This means that no image that thumbor generates will have a width
smaller than MIN\_WIDTH or height smaller than MIN\_HEIGHT.

i.e.:

::

    MIN_WIDTH = 1
    MIN_HEIGHT = 1

QUALITY
~~~~~~~

This option defines the quality that JPEG images will be generated with.
It defaults to 80.

i.e.: QUALITY = 90

MAX\_AGE
~~~~~~~~

This option defines the number of seconds that images should remain in
the browser's cache. It relates directly with the Expires and
Cache-Control headers.

i.e.: MAX\_AGE = 24 \* 60 \* 60 # A day of caching

MAX\_AGE\_TEMP\_IMAGE
~~~~~~~~~~~~~~~~~~~~~

When an image has some error in its detection or it has deferred
queueing, it's convenient to set a much lower expiration time for the
image cache. This way the browser will request the proper image faster.

This option defines the number of seconds that images in this scenario
should remain in the browser's cache. It relates directly with the
Expires and Cache-Control headers.

i.e.: MAX\_AGE\_TEMP\_IMAGE = 60 # A minute of caching

RESPECT\_ORIENTATION
~~~~~~~~~~~~~~~~~~~~

If this option is set to True, thumbor will reorient the image according
to it's EXIF Orientation tag (if one can be found). This options
defaults to False.

The operations performed in the image are as follow (considering the
value of the Orientation EXIF tag):

1. Nothing
2. Flips the image horizontally
3. Rotates the image 180 degrees
4. Flips the image vertically
5. Flips the image vertically and rotates 270 degrees
6. Rotates the image 270 degrees
7. Flips the image horizontally and rotates 270 degrees
8. Rotates the image 90 degrees

i.e.: RESPECT\_ORIENTATION = False

ALLOW\_ANIMATED\_GIFS
~~~~~~~~~~~~~~~~~~~~~

This option indicates whether animated gifs should be supported.

i.e.: ``ALLOW_ANIMATED_GIFS = True``

USE\_GIFSICLE\_ENGINE
~~~~~~~~~~~~~~~~~~~~~

This option indicates whether
`gifsicle <http://www.lcdf.org/gifsicle/man.html>`__ should be used for
all gif images, instead of the actual imaging engine. This defaults to
False.

**When using gifsicle thumbor will generate proper animated gifs, as
well as static gifs with the smallest possible size.**

i.e.: ``USE_GIFSICLE_ENGINE = True``

WARNING: When using gifsicle engine, filters will be skipped. Thumbor
will not do smart cropping as well.

AUTO\_WEBP
~~~~~~~~~~

This option indicates whether thumbor should send WebP images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "image/webp".

i.e.: ``AUTO_WEBP = True``

Queueing - Redis
----------------

REDIS\_QUEUE\_SERVER\_HOST
~~~~~~~~~~~~~~~~~~~~~~~~~~

Server host for the queued redis detector.

i.e.: ``REDIS_QUEUE_SERVER_HOST = 'localhost'``

REDIS\_QUEUE\_SERVER\_PORT
~~~~~~~~~~~~~~~~~~~~~~~~~~

Server port for the queued redis detector.

i.e.: ``REDIS_QUEUE_SERVER_PORT = 6379``

REDIS\_QUEUE\_SERVER\_DB
~~~~~~~~~~~~~~~~~~~~~~~~

Server database index for the queued redis detector

i.e.: ``REDIS_QUEUE_SERVER_DB = 0``

REDIS\_QUEUE\_SERVER\_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Server password for the queued redis detector

i.e.: ``REDIS_QUEUE_SERVER_PASSWORD = None``

Queueing - Amazon SQS
---------------------


SQS\_QUEUE\_KEY\_ID
~~~~~~~~~~~~~~~~~~~

Amazon AWS key id.

i.e.: ``SQS_QUEUE_KEY_ID = None``

SQS\_QUEUE\_KEY\_SECRET
~~~~~~~~~~~~~~~~~~~~~~~

Amazon AWS key secret.

i.e.: ``SQS_QUEUE_KEY_SECRET = None``

SQS\_QUEUE\_REGION
~~~~~~~~~~~~~~~~~~

Amazon AWS SQS region.

i.e.: ``SQS_QUEUE_REGION = 'us-east-1'``

Security Section
----------------

SECURITY\_KEY
~~~~~~~~~~~~~

This option specifies the security key that thumbor uses to sign secure
URLs.

i.e.: 1234567890123456

ALLOW\_UNSAFE\_URL
~~~~~~~~~~~~~~~~~~

This option specifies that the /unsafe url should be available in this
thumbor instance. It is boolean (True or False).

ALLOW\_OLD\_URLS
~~~~~~~~~~~~~~~~

This option specifies that the format prior to [[3.0.0-release-changes]]
should be allowed. It defaults to True.

**THIS OPTION IS DEPRECATED AND WILL DEFAULT TO FALSE IN THE NEXT
MAJOR.**

Loader Options Section
----------------------

FILE\_LOADER\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~

In case you are using thumbor's built-in file loader, this is the option
that allows you to specify where to find the images.

HTTP\_LOADER\_DEFAULT\_USER\_AGENT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option allows users to specify the default user-agent that thumbor
will send when requesting images with the HTTP Loader. Defaults to
'Thumbor/' (like Thumbor/3.10.0).

HTTP\_LOADER\_FORWARD\_USER\_AGENT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option tells thumbor to forward the request user agent when
requesting images using the HTTP Loader. Defaults to False.

Storage Options Section
-----------------------

STORAGE\_EXPIRATION\_SECONDS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This options specifies the default expiration time in seconds for the
storage.

i.e.: 60 (1 minute)

STORES\_CRYPTO\_KEY\_FOR\_EACH\_IMAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies whether thumbor should store the key for each
image (thus allowing the image to be found even if the security key
changes). This is a boolean flag (True or False).

File Storage Section
--------------------

FILE\_STORAGE\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~

In case you are using thumbor's built-in file storage, this is the
option that allows you to specify where to save the images.

MongoDB Storage Section
-----------------------

MONGO\_STORAGE\_SERVER\_HOST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the option that specifies the host for mongodb.

i.e.: 127.0.0.1

MONGO\_STORAGE\_SERVER\_PORT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the option that specifies the port where mongodb is running in.

i.e.: 27017

MONGO\_STORAGE\_SERVER\_DB
~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the option that specifies the database for mongodb.

i.e.: thumbor

MONGO\_STORAGE\_SERVER\_COLLECTION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the option that specifies the collection for thumbor's
documents.

i.e.: images

Redis Storage Section
---------------------

REDIS\_STORAGE\_SERVER\_HOST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the host server for Redis.

i.e.: localhost

REDIS\_STORAGE\_SERVER\_PORT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the port that redis is listening in.

i.e.: 6379

REDIS\_STORAGE\_SERVER\_DB
~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the database that thumbor should use.

i.e.: 0

REDIS\_STORAGE\_SERVER\_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the password that thumbor should use to
authenticate with redis.

i.e.: my-redis-password

Memcached Storage Section
-------------------------

MEMCACHE\_STORAGE\_SERVERS
~~~~~~~~~~~~~~~~~~~~~~~~~~

List of Memcache storage server hosts.

i.e.: ``MEMCACHE_STORAGE_SERVERS = ['localhost:11211']``

Result Storage Section
----------------------

RESULT\_STORAGE\_EXPIRATION\_SECONDS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Expiration in seconds of generated images in the result storage.

i.e.: ``RESULT_STORAGE_EXPIRATION_SECONDS = 0``

RESULT\_STORAGE\_FILE\_STORAGE\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Path where the Result storage will store generated images.

i.e.:
``RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/result_storage'``

RESULT\_STORAGE\_STORES\_UNSAFE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Indicates whether unsafe requests should also be stored in the Result
Storage.

i.e.: ``RESULT_STORAGE_STORES_UNSAFE = False``

Logging
-------

THUMBOR\_LOG\_FORMAT
~~~~~~~~~~~~~~~~~~~~

This option specifies the format to be used by logging messages sent
from thumbor.

i.e.: '%(asctime)s %(name)s:%(levelname)s %(message)s'

THUMBOR\_LOG\_DATE\_FORMAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the date format to be used by logging messages
sent from thumbor.

i.e.: '%Y-%m-%d %H:%M:%S'

Error Handling
--------------

USE\_CUSTOM\_ERROR\_HANDLING
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This configuration indicates whether thumbor should use a custom error
handler.

i.e.: ``USE_CUSTOM_ERROR_HANDLING = False``

ERROR\_HANDLER\_MODULE
~~~~~~~~~~~~~~~~~~~~~~

Error reporting module. Needs to contain a class called ErrorHandler
with a handle\_error(context, handler, exception) method.

i.e.: ``ERROR_HANDLER_MODULE = 'thumbor.error_handlers.sentry'``

Error Handling - Sentry
-----------------------

SENTRY\_DSN\_URL
~~~~~~~~~~~~~~~~

Sentry thumbor project dsn. i.e.:
http://5a63d58ae7b94f1dab3dee740b301d6a:73eea45d3e8649239a973087e8f21f98@localhost:9000/2

i.e.: ``SENTRY_DSN_URL = ''``

Upload
------

UPLOAD\_MAX\_SIZE
~~~~~~~~~~~~~~~~~

Max size in Kb for images uploaded to thumbor.

i.e.: ``UPLOAD_MAX_SIZE = 0``

UPLOAD\_ENABLED
~~~~~~~~~~~~~~~

Indicates whether thumbor should enable File uploads.

i.e.: ``UPLOAD_ENABLED = False``

UPLOAD\_PHOTO\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~

The type of storage to store uploaded images with.

i.e.: ``UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'``

UPLOAD\_DELETE\_ALLOWED
~~~~~~~~~~~~~~~~~~~~~~~

Indicates whether image deletion should be allowed.

i.e.: ``UPLOAD_DELETE_ALLOWED = False``

UPLOAD\_PUT\_ALLOWED
~~~~~~~~~~~~~~~~~~~~

Indicates whether image overwrite should be allowed.

i.e.: ``UPLOAD_PUT_ALLOWED = False``

UPLOAD\_DEFAULT\_FILENAME
~~~~~~~~~~~~~~~~~~~~~~~~~

Default filename for image uploaded.

i.e.: ``UPLOAD_DEFAULT_FILENAME = 'image'``

Example of Configuration File
-----------------------------

.. code:: python

    ################################### Logging ####################################

    ## Log Format to be used by thumbor when writing log messages.
    ## Defaults to: %(asctime)s %(name)s:%(levelname)s %(message)s
    #THUMBOR_LOG_FORMAT = '%(asctime)s %(name)s:%(levelname)s %(message)s'

    ## Date Format to be used by thumbor when writing log messages.
    ## Defaults to: %Y-%m-%d %H:%M:%S
    #THUMBOR_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    ################################################################################


    ################################### Imaging ####################################

    ## Max width in pixels for images read or generated by thumbor
    ## Defaults to: 0
    #MAX_WIDTH = 0

    ## Max height in pixels for images read or generated by thumbor
    ## Defaults to: 0
    #MAX_HEIGHT = 0

    ## Min width in pixels for images read or generated by thumbor
    ## Defaults to: 1
    #MIN_WIDTH = 1

    ## Min width in pixels for images read or generated by thumbor
    ## Defaults to: 1
    #MIN_HEIGHT = 1

    ## Allowed domains for the http loader to download. These are regular
    ## expressions.
    ## Defaults to: []
    #ALLOWED_SOURCES = #    [
    #    ]


    ## Quality index used for generated JPEG images
    ## Defaults to: 80
    #QUALITY = 80

    ## Max AGE sent as a header for the image served by thumbor in seconds
    ## Set to False to disable setting of Expires and Cache-Control headers
    ## Defaults to: 86400
    #MAX_AGE = 86400

    ## Indicates the Max AGE header in seconds for temporary images (images that
    ## haven't been detected yet)
    ## Defaults to: 0
    #MAX_AGE_TEMP_IMAGE = 0

    ## Indicates whether thumbor should rotate images that have an Orientation EXIF
    ## header
    ## Defaults to: False
    #RESPECT_ORIENTATION = False

    ## Indicates whether thumbor should enable the EXPERIMENTAL support for animated
    ## gifs.
    ## Defaults to: True
    #ALLOW_ANIMATED_GIFS = True

    ################################################################################


    ################################ Extensibility #################################

    ## The loader thumbor should use to load the original image. This must be the
    ## full name of a python module (python must be able to import it)
    ## Defaults to: thumbor.loaders.http_loader
    #LOADER = 'thumbor.loaders.http_loader'

    ## The file storage thumbor should use to store original images. This must be the
    ## full name of a python module (python must be able to import it)
    ## Defaults to: thumbor.storages.file_storage
    #STORAGE = 'thumbor.storages.file_storage'

    ## The result storage thumbor should use to store generated images. This must be
    ## the full name of a python module (python must be able to import it)
    ## Defaults to: None
    #RESULT_STORAGE = None

    ## The imaging engine thumbor should use to perform image operations. This must
    ## be the full name of a python module (python must be able to import it)
    ## Defaults to: thumbor.engines.pil
    #ENGINE = 'thumbor.engines.pil'

    ################################################################################


    ################################### Security ###################################

    ## The security key thumbor uses to sign image URLs
    ## Defaults to: MY_SECURE_KEY
    #SECURITY_KEY = 'MY_SECURE_KEY'

    ## Indicates if the /unsafe URL should be available
    ## Defaults to: True
    #ALLOW_UNSAFE_URL = True

    ## Indicates if encrypted (old style) URLs should be allowed
    ## Defaults to: True
    #ALLOW_OLD_URLS = True

    ################################################################################


    ################################# File Loader ##################################

    ## The root path where the File Loader will try to find images
    ## Defaults to: /tmp
    #FILE_LOADER_ROOT_PATH = '/tmp'

    ################################################################################


    ################################# File Storage #################################

    ## Expiration in seconds for the images in the File Storage. Defaults to one
    ## month
    ## Defaults to: 2592000
    #STORAGE_EXPIRATION_SECONDS = 2592000

    ## Indicates whether thumbor should store the signing key for each image in the
    ## file storage. This allows the key to be changed and old images to still be
    ## properly found
    ## Defaults to: False
    #STORES_CRYPTO_KEY_FOR_EACH_IMAGE = False

    ## The root path where the File Storage will try to find images
    ## Defaults to: /var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/thumbor/storage
    #FILE_STORAGE_ROOT_PATH = '/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/thumbor/storage'

    ################################################################################


    #################################### Upload ####################################

    ## Max size in Kb for images uploaded to thumbor
    ## Aliases: MAX_SIZE
    ## Defaults to: 0
    #UPLOAD_MAX_SIZE = 0

    ## Indicates whether thumbor should enable File uploads
    ## Aliases: ENABLE_ORIGINAL_PHOTO_UPLOAD
    ## Defaults to: False
    #UPLOAD_ENABLED = False

    ## The type of storage to store uploaded images with
    ## Aliases: ORIGINAL_PHOTO_STORAGE
    ## Defaults to: thumbor.storages.file_storage
    #UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'

    ## Indicates whether image deletion should be allowed
    ## Aliases: ALLOW_ORIGINAL_PHOTO_DELETION
    ## Defaults to: False
    #UPLOAD_DELETE_ALLOWED = False

    ## Indicates whether image overwrite should be allowed
    ## Aliases: ALLOW_ORIGINAL_PHOTO_PUTTING
    ## Defaults to: False
    #UPLOAD_PUT_ALLOWED = False

    ## Default filename for image uploaded
    ## Defaults to: image
    #UPLOAD_DEFAULT_FILENAME = 'image'

    ################################################################################


    ############################### MongoDB Storage ################################

    ## MongoDB storage server host
    ## Defaults to: localhost
    #MONGO_STORAGE_SERVER_HOST = 'localhost'

    ## MongoDB storage server port
    ## Defaults to: 27017
    #MONGO_STORAGE_SERVER_PORT = 27017

    ## MongoDB storage server database name
    ## Defaults to: thumbor
    #MONGO_STORAGE_SERVER_DB = 'thumbor'

    ## MongoDB storage image collection
    ## Defaults to: images
    #MONGO_STORAGE_SERVER_COLLECTION = 'images'

    ################################################################################


    ################################ Redis Storage #################################

    ## Redis storage server host
    ## Defaults to: localhost
    #REDIS_STORAGE_SERVER_HOST = 'localhost'

    ## Redis storage server port
    ## Defaults to: 6379
    #REDIS_STORAGE_SERVER_PORT = 6379

    ## Redis storage database index
    ## Defaults to: 0
    #REDIS_STORAGE_SERVER_DB = 0

    ## Redis storage server password
    ## Defaults to: None
    #REDIS_STORAGE_SERVER_PASSWORD = None

    ################################################################################


    ############################### Memcache Storage ###############################

    ## List of Memcache storage server hosts
    ## Defaults to: ['localhost:11211']
    #MEMCACHE_STORAGE_SERVERS = #    [
    #        'localhost:11211',
    #    ]


    ################################################################################


    ################################ Mixed Storage #################################

    ## Mixed Storage file storage. This must be the full name of a python module
    ## (python must be able to import it)
    ## Defaults to: thumbor.storages.no_storage
    #MIXED_STORAGE_FILE_STORAGE = 'thumbor.storages.no_storage'

    ## Mixed Storage signing key storage. This must be the full name of a python
    ## module (python must be able to import it)
    ## Defaults to: thumbor.storages.no_storage
    #MIXED_STORAGE_CRYPTO_STORAGE = 'thumbor.storages.no_storage'

    ## Mixed Storage detector information storage. This must be the full name of a
    ## python module (python must be able to import it)
    ## Defaults to: thumbor.storages.no_storage
    #MIXED_STORAGE_DETECTOR_STORAGE = 'thumbor.storages.no_storage'

    ################################################################################


    ##################################### Meta #####################################

    ## The callback function name that should be used by the META route for JSONP
    ## access
    ## Defaults to: None
    #META_CALLBACK_NAME = None

    ################################################################################


    ################################## Detection ###################################

    ## List of detectors that thumbor should use to find faces and/or features. All
    ## of them must be full names of python modules (python must be able to import
    ## it)
    ## Defaults to: []
    #DETECTORS = #    [
    #    ]


    ## The cascade file that opencv will use to detect faces
    ## Defaults to: haarcascade_frontalface_alt.xml
    #FACE_DETECTOR_CASCADE_FILE = 'haarcascade_frontalface_alt.xml'

    ################################################################################


    ################################### Filters ####################################

    ## List of filters that thumbor will allow to be used in generated images. All of
    ## them must be full names of python modules (python must be able to import
    ## it)
    ## Defaults to: []
    #FILTERS = #    [
    #    ]


    ################################################################################


    ################################ Result Storage ################################

    ## Expiration in seconds of generated images in the result storage
    ## Defaults to: 0
    #RESULT_STORAGE_EXPIRATION_SECONDS = 0

    ## Path where the Result storage will store generated images
    ## Defaults to: /var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/thumbor/result_storage
    #RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/var/folders/th/z6vmj34j1gngpvwl5fg5t9440000gp/T/thumbor/result_storage'

    ## Indicates whether unsafe requests should also be stored in the Result Storage
    ## Defaults to: False
    #RESULT_STORAGE_STORES_UNSAFE = False

    ################################################################################


    ############################ Queued Redis Detector #############################

    ## Server host for the queued redis detector
    ## Defaults to: localhost
    #REDIS_QUEUE_SERVER_HOST = 'localhost'

    ## Server port for the queued redis detector
    ## Defaults to: 6379
    #REDIS_QUEUE_SERVER_PORT = 6379

    ## Server database index for the queued redis detector
    ## Defaults to: 0
    #REDIS_QUEUE_SERVER_DB = 0

    ## Server password for the queued redis detector
    ## Defaults to: None
    #REDIS_QUEUE_SERVER_PASSWORD = None

    ################################################################################


    ############################# Queued SQS Detector ##############################

    ## AWS key id
    ## Defaults to: None
    #SQS_QUEUE_KEY_ID = None

    ## AWS key secret
    ## Defaults to: None
    #SQS_QUEUE_KEY_SECRET = None

    ## AWS SQS region
    ## Defaults to: us-east-1
    #SQS_QUEUE_REGION = 'us-east-1'

    ################################################################################


    #################################### Errors ####################################

    ## This configuration indicates whether thumbor should use a custom error
    ## handler.
    ## Defaults to: False
    #USE_CUSTOM_ERROR_HANDLING = False

    ## Error reporting module. Needs to contain a class called ErrorHandler with a
    ## handle_error(context, handler, exception) method.
    ## Defaults to: thumbor.error_handlers.sentry
    #ERROR_HANDLER_MODULE = 'thumbor.error_handlers.sentry'

    ################################################################################


    ############################### Errors - Sentry ################################

    ## Sentry thumbor project dsn. i.e.: http://5a63d58ae7b94f1dab3dee740b301d6a:73ee
    ## a45d3e8649239a973087e8f21f98@localhost:9000/2
    ## Defaults to:
    #SENTRY_DSN_URL = ''

    ################################################################################

