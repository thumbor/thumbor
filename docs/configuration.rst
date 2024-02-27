Configuration
=============

thumbor's configuration file is just a regular python script that
gets loaded by thumbor.

In order to get a commented configuration file, just run:

::

    thumbor-config > ./thumbor.conf

Override config through environment variable
-----------------------------------------------

It is possible override **string configs** through environment variables.
This is possible because thumbor uses `derpconf <https://github.com/globocom/derpconf>`__
to abstract loading configuration and derpconf allows this.

Extensibility Section
---------------------

LOADER
~~~~~~

The loader is responsible for retrieving the source image that thumbor
will work with. This configuration defines the module that thumbor will
use for it. **This must be a full namespace module (a.k.a. python has to
be able to *import* it).**

.. code:: python

   LOADER = 'thumbor.loaders.http_loader'

STORAGE
~~~~~~~

The storage is responsible for storing the source image bytes and
related metadata (face-detection, encryption and such) so that we don't
keep loading it every time. **This must be a full namespace module
(a.k.a. python has to be able to *import* it).**

.. code:: python

   STORAGE = 'thumbor.storages.file_storage'

MIXED\_STORAGE\_FILE\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(``thumbor.storages.mixed_storage``), this is where you specify the storage
that will be used to store images. **This must be a full namespace
module (a.k.a. python has to be able to *import* it).**

.. code:: python

   MIXED_STORAGE_FILE_STORAGE = 'thumbor.storages.file_storage'

MIXED\_STORAGE\_CRYPTO\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(``thumbor.storages.mixed_storage``), this is where you specify the storage
that will be used to store cryptography information. **This must be a
full namespace module (a.k.a. python has to be able to *import* it).**

.. code:: python

   MIXED_STORAGE_CRYPTO_STORAGE = 'thumbor.storages.file_storage'

MIXED\_STORAGE\_DETECTOR\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using thumbor's mixed storage
(``thumbor.storages.mixed_storage``), this is where you specify the storage
that will be used to store facial and feature detection results. **This
must be a full namespace module (a.k.a. python has to be able to
*import* it)**.

.. code:: python

   MIXED_STORAGE_DETECTOR_STORAGE = 'thumbor.storages.file_storage'

RESULT\_STORAGE
~~~~~~~~~~~~~~~

The result storage is responsible for storing the resulting image with
the specified parameters (think of it as a cache), so that we don't keep
processing it every time a request comes in. **This must be a full
namespace module (a.k.a. python has to be able to *import* it).**

.. code:: python

   RESULT_STORAGE = 'thumbor.result_storages.file_storage'

ENGINE
~~~~~~

The engine is responsible for transforming the image. **This must be a
full namespace module (a.k.a. python has to be able to *import* it).**

Currently, thumbor ships with only the ``thumbor.engines.pil`` imaging engine. A few years ago we conducted a comparison between the engines and there was no clear winner. Given PIL was the engine we were using at the time, we decided to stick with it. Other open source engines exist and you can find more about them in the plug-in section of the docs.

.. code:: python

   ENGINE = 'thumbor.engines.pil'

URL\_SIGNER
~~~~~~~~~~~

The url signer is responsible for validation and signing of requests to prevent url tampering,
which could lead to denial of service (example: filling the result_storage by specifying a different size).
**This must be a full namespace module (a.k.a. python has to be able to *import* it).**

.. code:: python

   URL_SIGNER = 'libthumbor.url_signers.base64_hmac_sha1'

Filters Section
---------------

In order to specify the filters that thumbor will use, you need a
configuration key called ``FILTERS``. This is a regular python list with the
full names (names that python can import) of the filter modules you want
to use.

i.e.:

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

.. code:: python

   META_CALLBACK_NAME = 'thumbor_callback'  # Or None for no callback

Face and Feature Detection Section
----------------------------------

DETECTORS
~~~~~~~~~

This options specifies the detectors that should run the image to check
for focal points.

i.e.:

.. code:: python

    DETECTORS = [
      'thumbor.detectors.face_detector',
      'thumbor.detectors.feature_detector'
   ]

Cascade Files
~~~~~~~~~~~~~

This option specifies the cascade (XML) file paths to train openCV to
find faces or other objects.

.. code:: python

   ## The cascade file that opencv will use to detect faces.
   FACE_DETECTOR_CASCADE_FILE = 'haarcascade_frontalface_alt.xml'

   ## The cascade file that opencv will use to detect glasses.
   GLASSES_DETECTOR_CASCADE_FILE = 'haarcascade_eye_tree_eyeglasses.xml'

   ## The cascade file that opencv will use to detect profile faces.
   PROFILE_DETECTOR_CASCADE_FILE = 'haarcascade_profileface.xml'


Imaging Section
---------------

ALLOWED\_SOURCES
~~~~~~~~~~~~~~~~

This configuration defines the source of the images that thumbor will
load. This is only used in the HttpLoader (check the LOADER
configuration above).

.. code:: python

   ALLOWED_SOURCES=['http://s.glbimg.com']

Another example with wildcards:

.. code:: python

   ALLOWED_SOURCES=['.+\.globo\.com', '.+\.glbimg\.com']

This is to get any images that are in ``*.globo.com`` or ``*.glbimg.com`` and it
will fail with any other domains.

ACCESS\_CONTROL\_ALLOW\_ORIGIN\_HEADER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This allows to send the ACCESS_CONTROL_ALLOW_ORIGIN header. For example,
if you want to tell the browser to allow code from any origin to
access your thumbor resources:

.. code:: python

   ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = '*'

If you want restrict access to a certain resource:

.. code:: python

   ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = 'https://www.example.com'

Not set by default.

MAX\_WIDTH and MAX\_HEIGHT
~~~~~~~~~~~~~~~~~~~~~~~~~~

These define the box that the resulting image for thumbor must fit-in.
This means that no image that thumbor generates will have a width larger
than MAX\_WIDTH or height larger than MAX\_HEIGHT. It defaults to 0, which
means there is not limit. If the original image is larger than
MAX\_WIDTH x MAX\_HEIGHT, it is proportionally resized to MAX\_WIDTH x MAX\_HEIGHT.

.. code:: python

    MAX_WIDTH = 1200
    MAX_HEIGHT = 800

MIN\_WIDTH and MIN\_HEIGHT
~~~~~~~~~~~~~~~~~~~~~~~~~~

These define the box that the resulting image for thumbor must fit-in.
This means that no image that thumbor generates will have a width
smaller than MIN\_WIDTH or height smaller than MIN\_HEIGHT. It defaults to 1.
If the original image is smaller than  MIN\_WIDTH x MIN\_HEIGHT, it is
proportionally resized to MIN\_WIDTH x MIN\_HEIGHT.

.. code:: python

    MIN_WIDTH = 1
    MIN_HEIGHT = 1

QUALITY
~~~~~~~

This option defines the quality that JPEG images will be generated with.
It defaults to 80.

.. code:: python

   QUALITY = 90

MAX\_AGE
~~~~~~~~

This option defines the number of seconds that images should remain in
the browser's cache. It relates directly with the Expires and
Cache-Control headers.

.. code:: python

   MAX_AGE = 24 * 60 * 60  # A day of caching

MAX\_AGE\_TEMP\_IMAGE
~~~~~~~~~~~~~~~~~~~~~

When an image has some error in its detection or it has deferred
queueing, it's convenient to set a much lower expiration time for the
image cache. This way the browser will request the proper image faster.

This option defines the number of seconds that images in this scenario
should remain in the browser's cache. It relates directly with the
Expires and Cache-Control headers.

.. code:: python

   MAX_AGE_TEMP_IMAGE = 60  # A minute of caching

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

.. code:: python

   RESPECT_ORIENTATION = False

ALLOW\_ANIMATED\_GIFS
~~~~~~~~~~~~~~~~~~~~~

This option indicates whether animated gifs should be supported.

.. code:: python

   ALLOW_ANIMATED_GIFS = True

USE\_GIFSICLE\_ENGINE
~~~~~~~~~~~~~~~~~~~~~

This option indicates whether
`gifsicle <http://www.lcdf.org/gifsicle/man.html>`__ should be used for
all gif images, instead of the actual imaging engine. This defaults to
False.

**When using gifsicle thumbor will generate proper animated gifs, as
well as static gifs with the smallest possible size.**

.. code:: python

   USE_GIFSICLE_ENGINE = True

WARNING: When using gifsicle engine, filters will be skipped, except for `cover()` filter. thumbor
will not do smart cropping as well.

AUTO_*
~~~~~~~~~~~~

These configurations indicates that thumbor will try to automatically convert
the image format to a lighter image format, according to this compression order:
`WEBP, AVIF, JPG, HEIF, PNG` — from highest (`WEBP`) to lowest (`PNG`) priority.

AUTO\_WEBP
^^^^^^^^^^

This option indicates whether thumbor should send WebP images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "image/webp".

.. code:: python

   AUTO_WEBP = True

AUTO\_AVIF
^^^^^^^^^^

This option indicates whether thumbor should send Avif images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "image/avif" and pillow-avif-plugin is enabled.

.. code:: python

   AUTO_AVIF = True

AUTO\_PNG\_TO\_JPG
^^^^^^^^^^^^^^^^^^

This option indicates whether thumbor should transform PNG images
automatically to JPEG. If the image is a PNG without transparency and
the numpy dependency is installed, thumbor will transform from png to jpeg.
In the most of cases the image size will decrease.

WARNING: Depending on case, this is not a good deal. This transformation
maybe causes distortions or the size of image can increase.
Images with texts, for example, the result image maybe will be distorted.
Dark images, for example, the size of result image maybe will be bigger.
You have to evaluate the majority of your use cases to take a decision about the usage of this conf.

.. code:: python

   AUTO_PNG_TO_JPG = True

AUTO\_JPG
^^^^^^^^^

This option indicates whether thumbor should send JPG images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "*/*", "image/jpg" or "image/jpeg".

.. code:: python

   AUTO_JPG = True

AUTO\_PNG
^^^^^^^^^

This option indicates whether thumbor should send PNG images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "image/png".

.. code:: python

   AUTO_PNG = True

AUTO\_HEIF
^^^^^^^^^^

This option indicates whether thumbor should send Heif images
automatically if the request comes with an "Accept" header that
specifies that the browser supports "image/heif" and pillow-heif is enabled.

.. code:: python

   AUTO_HEIF = True

Queueing - Redis Single Node
----------------------------

REDIS\_QUEUE\_MODE
~~~~~~~~~~~~~~~~~~

Redis operation mode 'single_node' or 'sentinel'

.. code:: python

   REDIS_QUEUE_MODE = 'single_node'

REDIS\_QUEUE\_SERVER\_HOST
~~~~~~~~~~~~~~~~~~~~~~~~~~

Server host for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SERVER_HOST = 'localhost'

REDIS\_QUEUE\_SERVER\_PORT
~~~~~~~~~~~~~~~~~~~~~~~~~~

Server port for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SERVER_PORT = 6379

REDIS\_QUEUE\_SERVER\_DB
~~~~~~~~~~~~~~~~~~~~~~~~

Server database index for the queued redis detector

.. code:: python

   REDIS_QUEUE_SERVER_DB = 0

REDIS\_QUEUE\_SERVER\_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Server password for the queued redis detector

.. code:: python

   REDIS_QUEUE_SERVER_PASSWORD = None

Queueing - Redis Sentinel
-------------------------

REDIS\_QUEUE\_MODE
~~~~~~~~~~~~~~~~~~

Redis operation mode 'single_node' or 'sentinel'

.. code:: python

   REDIS_QUEUE_MODE = 'sentinel'

REDIS\_QUEUE\_SENTINEL\_INSTANCES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server instances for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_INSTANCES = 'localhost:23679,localhost:23680'

REDIS\_QUEUE\_SENTINEL\_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server password for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_PASSWORD = None

REDIS\_QUEUE\_SENTINEL\_MASTER\_INSTANCE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server master instance for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_MASTER_INSTANCE = 'masterinstance'

REDIS\_QUEUE\_SENTINEL\_MASTER\_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server master password for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_MASTER_PASSWORD = None

REDIS\_QUEUE\_SENTINEL\_MASTER\_DB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server master database index for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_MASTER_DB = 0

REDIS\_QUEUE\_SENTINEL\_SOCKET\_TIMEOUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sentinel server socket timeout for the queued redis detector.

.. code:: python

   REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT = 10.0

Queueing - Amazon SQS
---------------------

This queue will be removed in an upcoming release in favor of the open source AWS plug-ins for thumbor.

SQS\_QUEUE\_KEY\_ID
~~~~~~~~~~~~~~~~~~~

Amazon AWS key id.

.. code:: python

   SQS_QUEUE_KEY_ID = None

SQS\_QUEUE\_KEY\_SECRET
~~~~~~~~~~~~~~~~~~~~~~~

Amazon AWS key secret.

.. code:: python

   SQS_QUEUE_KEY_SECRET = None

SQS\_QUEUE\_REGION
~~~~~~~~~~~~~~~~~~

Amazon AWS SQS region.

.. code:: python

   SQS_QUEUE_REGION = 'us-east-1'

Security Section
----------------

SECURITY\_KEY
~~~~~~~~~~~~~

This option specifies the security key that thumbor uses to sign secure
URLs.

.. code:: python

   1234567890123456

ALLOW\_UNSAFE\_URL
~~~~~~~~~~~~~~~~~~

This option specifies that the /unsafe url should be available in this
thumbor instance. It is boolean (True or False).

.. warning::

   It is **STRONGLY** recommended that you turn off this flag in production environments as this can lead to DDoS attacks against thumbor.

.. code:: python

   ALLOW_UNSAFE_URL = False

Loader Options Section
----------------------

FILE\_LOADER\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~

In case you are using thumbor's built-in file loader, this is the option
that allows you to specify where to find the images.

.. code:: python

   FILE_LOADER_ROOT_PATH = "/home/thumbor/images"

HTTP\_LOADER\_DEFAULT\_USER\_AGENT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option allows users to specify the default user-agent that thumbor
will send when requesting images with the HTTP Loader. Defaults to
'thumbor/' (like thumbor/7.0.0).

.. code:: python

   HTTP_LOADER_DEFAULT_USER_AGENT = 'thumbor/7.0.0'


HTTP\_LOADER\_FORWARD\_USER\_AGENT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option tells thumbor to forward the request user agent when
requesting images using the HTTP Loader. Defaults to False.

.. code:: python

   HTTP_LOADER_FORWARD_USER_AGENT = False


Storage Options Section
-----------------------

STORAGE\_EXPIRATION\_SECONDS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This options specifies the default expiration time in seconds for the
storage.

.. code:: python

   STORAGE_EXPIRATION_SECONDS = 60  # 1 minute

STORES\_CRYPTO\_KEY\_FOR\_EACH\_IMAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies whether thumbor should store the key for each
image (thus allowing the image to be found even if the security key
changes). This is a boolean flag (True or False).

.. warning::

   If this flag is set to False, it essentially means that whenever you change the security key, for whatever reason, you just invalidated every single image that's been generated before.

   That may be ok if you have another service fetching stored images instead of allowing thumbor to do it (as many of thumbor users do).

.. code:: python

   STORAGE_CRYPTO_KEY_FOR_EACH_IMAGE = True


File Storage Section
--------------------

FILE\_STORAGE\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~

In case you are using thumbor's built-in file storage, this is the
option that allows you to specify where to save the images.

.. code:: python

   FILE_STORAGE_ROOT_PATH = '/home/thumbor/storage'

Result Storage Section
----------------------

RESULT\_STORAGE\_EXPIRATION\_SECONDS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Expiration in seconds of generated images in the result storage.

.. code:: python

   RESULT_STORAGE_EXPIRATION_SECONDS = 0

RESULT\_STORAGE\_FILE\_STORAGE\_ROOT\_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Path where the Result storage will store generated images.

.. code:: python

   RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/result_storage'

RESULT\_STORAGE\_STORES\_UNSAFE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Indicates whether unsafe requests should also be stored in the Result
Storage.

.. code:: python

   RESULT_STORAGE_STORES_UNSAFE = False

Healthcheck
-----------

HEALTHCHECK\_ROUTE
~~~~~~~~~~~~~~~~~~~~

The URL path to a healthcheck.  This will return a 200 and the text 'WORKING'.

.. code:: python

   HEALTHCHECK_ROUTE = '/status'

Will put the healthcheck response on ``http://host:port/status``

The default route is ``/healthcheck``.

Logging
-------

THUMBOR\_LOG\_FORMAT
~~~~~~~~~~~~~~~~~~~~

This option specifies the format to be used by logging messages sent
from thumbor.

.. code:: python

   THUMBOR_LOG_FORMAT = '%(asctime)s %(name)s:%(levelname)s %(message)s'

THUMBOR\_LOG\_DATE\_FORMAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

This option specifies the date format to be used by logging messages
sent from thumbor.

.. code:: python

   THUMBOR_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

Error Handling
--------------

USE\_CUSTOM\_ERROR\_HANDLING
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This configuration indicates whether thumbor should use a custom error
handler.

.. code:: python

   USE_CUSTOM_ERROR_HANDLING = False

ERROR\_HANDLER\_MODULE
~~~~~~~~~~~~~~~~~~~~~~

Error reporting module. Needs to contain a class called ErrorHandler
with a handle\_error(context, handler, exception) method.

.. code:: python

   ERROR_HANDLER_MODULE = 'thumbor.error_handlers.sentry'

Error Handling - Sentry
-----------------------

SENTRY\_DSN\_URL
~~~~~~~~~~~~~~~~

Sentry thumbor project dsn. i.e.:
http://5a63d58ae7b94f1dab3dee740b301d6a:73eea45d3e8649239a973087e8f21f98@localhost:9000/2

.. code:: python

   SENTRY_DSN_URL = ''

SENTRY\_ENVIRONMENT
~~~~~~~~~~~~~~~~~~~

Sentry thumbor environment.

.. code:: python

   SENTRY_ENVIRONMENT = 'staging'

Upload
------

UPLOAD\_MAX\_SIZE
~~~~~~~~~~~~~~~~~

Max size in bytes for images uploaded to thumbor.

.. code:: python

   UPLOAD_MAX_SIZE = 0

UPLOAD\_ENABLED
~~~~~~~~~~~~~~~

Indicates whether thumbor should enable File uploads.

.. code:: python

   UPLOAD_ENABLED = False

UPLOAD\_PHOTO\_STORAGE
~~~~~~~~~~~~~~~~~~~~~~

The type of storage to store uploaded images with.

.. code:: python

   UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'

UPLOAD\_DELETE\_ALLOWED
~~~~~~~~~~~~~~~~~~~~~~~

Indicates whether image deletion should be allowed.

.. code:: python

   UPLOAD_DELETE_ALLOWED = False

UPLOAD\_PUT\_ALLOWED
~~~~~~~~~~~~~~~~~~~~

Indicates whether image overwrite should be allowed.

.. code:: python

   UPLOAD_PUT_ALLOWED = False

UPLOAD\_DEFAULT\_FILENAME
~~~~~~~~~~~~~~~~~~~~~~~~~

Default filename for image uploaded.

.. code:: python

   UPLOAD_DEFAULT_FILENAME = 'image'

GC\_INTERVAL
~~~~~~~~~~~~

Set manual garbage collection interval in seconds. Defaults to None (no manual garbage collection). Try this if your thumbor is running out of memory. May cause an increase in CPU load.

.. code:: python

   GC_INTERVAL = 60

Example of Configuration File
-----------------------------

.. code:: python

   ################################### Logging ####################################

   ## Logging configuration as json
   ## Defaults to: None
   #THUMBOR_LOG_CONFIG = None

   ## Log Format to be used by thumbor when writing log messages.
   ## Defaults to: '%(asctime)s %(name)s:%(levelname)s %(message)s'
   #THUMBOR_LOG_FORMAT = '%(asctime)s %(name)s:%(levelname)s %(message)s'

   ## Date Format to be used by thumbor when writing log messages.
   ## Defaults to: '%Y-%m-%d %H:%M:%S'
   #THUMBOR_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

   ################################################################################


   ################################### Imaging ####################################

   ## Max width in pixels for images read or generated by thumbor
   ## Defaults to: 0
   #MAX_WIDTH = 0

   ## Max height in pixels for images read or generated by thumbor
   ## Defaults to: 0
   #MAX_HEIGHT = 0

   ## Max pixel count for images read by thumbor
   ## Defaults to: 75000000.0
   #MAX_PIXELS = 75000000.0

   ## Min width in pixels for images read or generated by thumbor
   ## Defaults to: 1
   #MIN_WIDTH = 1

   ## Min width in pixels for images read or generated by thumbor
   ## Defaults to: 1
   #MIN_HEIGHT = 1

   ## Allowed domains for the http loader to download. These are regular
   ## expressions.
   ## Defaults to: [
   #]

   #ALLOWED_SOURCES = [
   #]


   ## Quality index used for generated JPEG images
   ## Defaults to: 80
   #QUALITY = 80

   ## Exports JPEG images with the `progressive` flag set.
   ## Defaults to: True
   #PROGRESSIVE_JPEG = True

   ## Specify subsampling behavior for Pillow (see `subsampling`               in
   ## http://pillow.readthedocs.org/en/latest/handbook/image-file-
   ## formats.html#jpeg).Be careful to use int for 0,1,2 and string for "4:4:4"
   ## notation. Will ignore `quality`. Using `keep` will copy the original file's
   ## subsampling.
   ## Defaults to: None
   #PILLOW_JPEG_SUBSAMPLING = None

   ## Specify quantization tables for Pillow (see `qtables`               in
   ## http://pillow.readthedocs.org/en/latest/handbook/image-file-
   ## formats.html#jpeg). Will ignore `quality`. Using `keep` will copy the
   ## original file's qtables.
   ## Defaults to: None
   #PILLOW_JPEG_QTABLES = None

   ## Specify resampling filter for Pillow resize method.One of LANCZOS, NEAREST,
   ## BILINEAR, BICUBIC, HAMMING (Pillow>=3.4.0).
   ## Defaults to: 'LANCZOS'
   #PILLOW_RESAMPLING_FILTER = 'LANCZOS'

   ## Quality index used for generated WebP images. If not set (None) the same level
   ## of JPEG quality will be used. If 100 the `lossless` flag will be used.
   ## Defaults to: None
   #WEBP_QUALITY = None

   ## Compression level for generated PNG images.
   ## Defaults to: 6
   #PNG_COMPRESSION_LEVEL = 6

   ## Indicates if final image should preserve indexed mode (P or 1) of original
   ## image
   ## Defaults to: True
   #PILLOW_PRESERVE_INDEXED_MODE = True

   ## Specifies whether WebP format should be used automatically if the request
   ## accepts it (via Accept header)
   ## Defaults to: False
   #AUTO_WEBP = False

   ## Specifies whether a PNG image should be used automatically if the png image
   ## has no transparency (via alpha layer). WARNING: Depending on case, this is
   ## not a good deal. This transformation maybe causes distortions or the size
   ## of image can increase. Images with texts, for example, the result image
   ## maybe will be distorted. Dark images, for example, the size of result image
   ## maybe will be bigger. You have to evaluate the majority of your use cases
   ## to take a decision about the usage of this conf.
   ## Defaults to: False
   #AUTO_PNG_TO_JPG = False

   ## Specify the ratio between 1in and 1px for SVG images. This is only used
   ## whenrasterizing SVG images having their size units in cm or inches.
   ## Defaults to: 150
   #SVG_DPI = 150

   ## Max AGE sent as a header for the image served by thumbor in seconds
   ## Defaults to: 86400
   #MAX_AGE = 86400

   ## Indicates the Max AGE header in seconds for temporary images (images with
   ## failed smart detection)
   ## Defaults to: 0
   #MAX_AGE_TEMP_IMAGE = 0

   ## Indicates whether thumbor should rotate images that have an Orientation EXIF
   ## header
   ## Defaults to: False
   #RESPECT_ORIENTATION = False

   ## Ignore errors during smart detections and return image as a temp image (not
   ## saved in result storage and with MAX_AGE_TEMP_IMAGE age)
   ## Defaults to: False
   #IGNORE_SMART_ERRORS = False

   ## Sends If-Modified-Since & Last-Modified headers; requires support from result
   ## storage
   ## Defaults to: False
   #SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS = False

   ## Sends the Access-Control-Allow-Origin header
   #ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = '*'

   ## Preserves exif information in generated images. Increases image size in
   ## kbytes, use with caution.
   ## Defaults to: False
   #PRESERVE_EXIF_INFO = False

   ## Indicates whether thumbor should enable the EXPERIMENTAL support for animated
   ## gifs.
   ## Defaults to: True
   #ALLOW_ANIMATED_GIFS = True

   ## Indicates whether thumbor should use gifsicle engine. Please note that smart
   ## cropping and filters are not supported for gifs using gifsicle (but won't
   ## give an error).
   ## Defaults to: False
   #USE_GIFSICLE_ENGINE = False

   ## Indicates whether thumbor should enable blacklist functionality to prevent
   ## processing certain images.
   ## Defaults to: False
   #USE_BLACKLIST = False

   ## Size of the thread pool used for image transformations. The default value is 0
   ## (don't use a threadpoool. Increase this if you are seeing your IOLoop
   ## getting blocked (often indicated by your upstream HTTP requests timing out)
   ## Defaults to: 0
   #ENGINE_THREADPOOL_SIZE = 0

   ################################################################################


   ################################# Extensibility #################################

   ## The metrics backend thumbor should use to measure internal actions. This must
   ## be the full name of a python module (python must be able to import it)
   ## Defaults to: 'thumbor.metrics.logger_metrics'
   #METRICS = 'thumbor.metrics.logger_metrics'

   ## The loader thumbor should use to load the original image. This must be the
   ## full name of a python module (python must be able to import it)
   ## Defaults to: 'thumbor.loaders.http_loader'
   #LOADER = 'thumbor.loaders.http_loader'

   ## The file storage thumbor should use to store original images. This must be the
   ## full name of a python module (python must be able to import it)
   ## Defaults to: 'thumbor.storages.file_storage'
   #STORAGE = 'thumbor.storages.file_storage'

   ## The result storage thumbor should use to store generated images. This must be
   ## the full name of a python module (python must be able to import it)
   ## Defaults to: None
   #RESULT_STORAGE = None

   ## The imaging engine thumbor should use to perform image operations. This must
   ## be the full name of a python module (python must be able to import it)
   ## Defaults to: 'thumbor.engines.pil'
   #ENGINE = 'thumbor.engines.pil'

   ## The gif engine thumbor should use to perform image operations. This must be
   ## the full name of a python module (python must be able to import it)
   ## Defaults to: 'thumbor.engines.gif'
   #GIF_ENGINE = 'thumbor.engines.gif'

   ## The url signer thumbor should use to verify url signatures.This must be the
   ## full name of a python module (python must be able to import it)
   ## Defaults to: 'libthumbor.url_signers.base64_hmac_sha1'
   #URL_SIGNER = 'libthumbor.url_signers.base64_hmac_sha1'

   ################################################################################


   ################################### Security ###################################

   ## The security key thumbor uses to sign image URLs
   ## Defaults to: 'MY_SECURE_KEY'
   #SECURITY_KEY = 'MY_SECURE_KEY'

   ## Indicates if the /unsafe URL should be available
   ## Defaults to: True
   #ALLOW_UNSAFE_URL = True

   ################################################################################


   ##################################### HTTP #####################################

   ## Enables automatically generated etags
   ## Defaults to: True
   #ENABLE_ETAGS = True

   ################################################################################


   ################################### Storage ####################################

   ## Set maximum id length for images when stored
   ## Defaults to: 32
   #MAX_ID_LENGTH = 32

   ################################################################################


   ################################# Performance ##################################

   ## Set garbage collection interval in seconds
   ## Defaults to: None
   #GC_INTERVAL = None

   ################################################################################


   ################################# Healthcheck ##################################

   ## Healthcheck route.
   ## Defaults to: '/healthcheck'
   #HEALTHCHECK_ROUTE = '/healthcheck'

   ################################################################################


   ################################### Metrics ####################################

   ## Host to send statsd instrumentation to
   ## Defaults to: None
   #STATSD_HOST = None

   ## Port to send statsd instrumentation to
   ## Defaults to: 8125
   #STATSD_PORT = 8125

   ## Prefix for statsd
   ## Defaults to: None
   #STATSD_PREFIX = None

   ################################################################################


   ################################# File Loader ##################################

   ## The root path where the File Loader will try to find images
   ## Defaults to: '/home/heynemann'
   #FILE_LOADER_ROOT_PATH = '/home/heynemann'

   ################################################################################


   ################################# HTTP Loader ##################################

   ## The maximum number of seconds libcurl can take to connect to an image being
   ## loaded
   ## Defaults to: 5
   #HTTP_LOADER_CONNECT_TIMEOUT = 5

   ## The maximum number of seconds libcurl can take to download an image
   ## Defaults to: 20
   #HTTP_LOADER_REQUEST_TIMEOUT = 20

   ## Indicates whether libcurl should follow redirects when downloading an image
   ## Defaults to: True
   #HTTP_LOADER_FOLLOW_REDIRECTS = True

   ## Indicates the number of redirects libcurl should follow when downloading an
   ## image
   ## Defaults to: 5
   #HTTP_LOADER_MAX_REDIRECTS = 5

   ## The maximum number of simultaneous HTTP connections the loader can make before
   ## queuing
   ## Defaults to: 10
   #HTTP_LOADER_MAX_CLIENTS = 10

   ## Indicates whether thumbor should forward the user agent of the requesting user
   ## Defaults to: False
   #HTTP_LOADER_FORWARD_USER_AGENT = False

   ## Indicates whether thumbor should forward the headers of the request
   ## Defaults to: False
   #HTTP_LOADER_FORWARD_ALL_HEADERS = False

   ## Indicates which headers should be forwarded among all the headers of the
   ## request
   ## Defaults to: [
   #]

   #HTTP_LOADER_FORWARD_HEADERS_WHITELIST = [
   #]


   ## Default user agent for thumbor http loader requests
   ## Defaults to: 'Thumbor/6.7.1'
   #HTTP_LOADER_DEFAULT_USER_AGENT = 'Thumbor/6.7.1'

   ## The proxy host needed to load images through
   ## Defaults to: None
   #HTTP_LOADER_PROXY_HOST = None

   ## The proxy port for the proxy host
   ## Defaults to: None
   #HTTP_LOADER_PROXY_PORT = None

   ## The proxy username for the proxy host
   ## Defaults to: None
   #HTTP_LOADER_PROXY_USERNAME = None

   ## The proxy password for the proxy host
   ## Defaults to: None
   #HTTP_LOADER_PROXY_PASSWORD = None

   ## The filename of CA certificates in PEM format
   ## Defaults to: None
   #HTTP_LOADER_CA_CERTS = None

   ## Validate the server’s certificate for HTTPS requests
   ## Defaults to: None
   #HTTP_LOADER_VALIDATE_CERTS = None

   ## The filename for client SSL key
   ## Defaults to: None
   #HTTP_LOADER_CLIENT_KEY = None

   ## The filename for client SSL certificate
   ## Defaults to: None
   #HTTP_LOADER_CLIENT_CERT = None

   ## If the CurlAsyncHTTPClient should be used
   ## Defaults to: False
   #HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT = False

   ################################################################################


   ################################### General ####################################

   ## If HTTP_LOADER_CURL_LOW_SPEED_LIMIT and HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT are
   ## set, then this is the time in seconds as integer after a download should
   ## timeout if the speed is below HTTP_LOADER_CURL_LOW_SPEED_LIMIT for that
   ## long
   ## Defaults to: 0
   #HTTP_LOADER_CURL_LOW_SPEED_TIME = 0

   ## If HTTP_LOADER_CURL_LOW_SPEED_TIME and HTTP_LOADER_CURL_ASYNC_HTTP_CLIENT are
   ## set, then this is the limit in bytes per second as integer which should
   ## timeout if the speed is below that limit for
   ## HTTP_LOADER_CURL_LOW_SPEED_TIME seconds
   ## Defaults to: 0
   #HTTP_LOADER_CURL_LOW_SPEED_LIMIT = 0

   ## Custom app class to override ThumborServiceApp. This config value is
   ## overridden by the -a command-line parameter.
   ## Defaults to: 'thumbor.app.ThumborServiceApp'
   #APP_CLASS = 'thumbor.app.ThumborServiceApp'

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
   ## Defaults to: '/tmp/thumbor/storage'
   #FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/storage'

   ################################################################################


   #################################### Upload ####################################

   ## Max size in bytes for images uploaded to thumbor
   ## Aliases: MAX_SIZE
   ## Defaults to: 0
   #UPLOAD_MAX_SIZE = 0

   ## Indicates whether thumbor should enable File uploads
   ## Aliases: ENABLE_ORIGINAL_PHOTO_UPLOAD
   ## Defaults to: False
   #UPLOAD_ENABLED = False

   ## The type of storage to store uploaded images with
   ## Aliases: ORIGINAL_PHOTO_STORAGE
   ## Defaults to: 'thumbor.storages.file_storage'
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
   ## Defaults to: 'image'
   #UPLOAD_DEFAULT_FILENAME = 'image'

   ################################################################################


   ################################# Mixed Storage #################################

   ## Mixed Storage file storage. This must be the full name of a python module
   ## (python must be able to import it)
   ## Defaults to: 'thumbor.storages.no_storage'
   #MIXED_STORAGE_FILE_STORAGE = 'thumbor.storages.no_storage'

   ## Mixed Storage signing key storage. This must be the full name of a python
   ## module (python must be able to import it)
   ## Defaults to: 'thumbor.storages.no_storage'
   #MIXED_STORAGE_CRYPTO_STORAGE = 'thumbor.storages.no_storage'

   ## Mixed Storage detector information storage. This must be the full name of a
   ## python module (python must be able to import it)
   ## Defaults to: 'thumbor.storages.no_storage'
   #MIXED_STORAGE_DETECTOR_STORAGE = 'thumbor.storages.no_storage'

   ################################################################################


   ##################################### Meta #####################################

   ## The callback function name that should be used by the META route for JSONP
   ## access
   ## Defaults to: None
   #META_CALLBACK_NAME = None

   ################################################################################


   ################################### Detection ###################################

   ## List of detectors that thumbor should use to find faces and/or features. All
   ## of them must be full names of python modules (python must be able to import
   ## it)
   ## Defaults to: [
   #]

   #DETECTORS = [
   #]


   ## The cascade file that opencv will use to detect faces.
   ## Defaults to: 'haarcascade_frontalface_alt.xml'
   #FACE_DETECTOR_CASCADE_FILE = 'haarcascade_frontalface_alt.xml'

   ## The cascade file that opencv will use to detect glasses.
   ## Defaults to: 'haarcascade_eye_tree_eyeglasses.xml'
   #GLASSES_DETECTOR_CASCADE_FILE = 'haarcascade_eye_tree_eyeglasses.xml'

   ## The cascade file that opencv will use to detect profile faces.
   ## Defaults to: 'haarcascade_profileface.xml'
   #PROFILE_DETECTOR_CASCADE_FILE = 'haarcascade_profileface.xml'

   ################################################################################


   ################################## Optimizers ##################################

   ## List of optimizers that thumbor will use to optimize images
   ## Defaults to: [
   #]

   #OPTIMIZERS = [
   #]


   ## Path for the jpegtran binary
   ## Defaults to: '/usr/bin/jpegtran'
   #JPEGTRAN_PATH = '/usr/bin/jpegtran'

   ## Path for the progressive scans file to use with jpegtran optimizer. Implies
   ## progressive jpeg output
   ## Defaults to: ''
   #JPEGTRAN_SCANS_FILE = ''

   ## Path for the ffmpeg binary used to generate gifv(h.264)
   ## Defaults to: '/usr/local/bin/ffmpeg'
   #FFMPEG_PATH = '/usr/local/bin/ffmpeg'

   ################################################################################


   ################################### Filters ####################################

   ## List of filters that thumbor will allow to be used in generated images. All of
   ## them must be full names of python modules (python must be able to import
   ## it)
   ## Defaults to: [
   #    'thumbor.filters.brightness',
   #    'thumbor.filters.colorize',
   #    'thumbor.filters.contrast',
   #    'thumbor.filters.rgb',
   #    'thumbor.filters.round_corner',
   #    'thumbor.filters.quality',
   #    'thumbor.filters.noise',
   #    'thumbor.filters.watermark',
   #    'thumbor.filters.equalize',
   #    'thumbor.filters.fill',
   #    'thumbor.filters.sharpen',
   #    'thumbor.filters.strip_exif',
   #    'thumbor.filters.strip_icc',
   #    'thumbor.filters.frame',
   #    'thumbor.filters.grayscale',
   #    'thumbor.filters.rotate',
   #    'thumbor.filters.format',
   #    'thumbor.filters.max_bytes',
   #    'thumbor.filters.convolution',
   #    'thumbor.filters.blur',
   #    'thumbor.filters.extract_focal',
   #    'thumbor.filters.focal',
   #    'thumbor.filters.no_upscale',
   #    'thumbor.filters.saturation',
   #    'thumbor.filters.max_age',
   #    'thumbor.filters.curve',
   #    'thumbor.filters.background_color',
   #    'thumbor.filters.upscale',
   #    'thumbor.filters.proportion',
   #    'thumbor.filters.stretch',
   #]

   #FILTERS = [
   #    'thumbor.filters.brightness',
   #    'thumbor.filters.colorize',
   #    'thumbor.filters.contrast',
   #    'thumbor.filters.rgb',
   #    'thumbor.filters.round_corner',
   #    'thumbor.filters.quality',
   #    'thumbor.filters.noise',
   #    'thumbor.filters.watermark',
   #    'thumbor.filters.equalize',
   #    'thumbor.filters.fill',
   #    'thumbor.filters.sharpen',
   #    'thumbor.filters.strip_exif',
   #    'thumbor.filters.strip_icc',
   #    'thumbor.filters.frame',
   #    'thumbor.filters.grayscale',
   #    'thumbor.filters.rotate',
   #    'thumbor.filters.format',
   #    'thumbor.filters.max_bytes',
   #    'thumbor.filters.convolution',
   #    'thumbor.filters.blur',
   #    'thumbor.filters.extract_focal',
   #    'thumbor.filters.focal',
   #    'thumbor.filters.no_upscale',
   #    'thumbor.filters.saturation',
   #    'thumbor.filters.max_age',
   #    'thumbor.filters.curve',
   #    'thumbor.filters.background_color',
   #    'thumbor.filters.upscale',
   #    'thumbor.filters.proportion',
   #    'thumbor.filters.stretch',
   #]


   ################################################################################


   ################################ Result Storage ################################

   ## Expiration in seconds of generated images in the result storage
   ## Defaults to: 0
   #RESULT_STORAGE_EXPIRATION_SECONDS = 0

   ## Path where the Result storage will store generated images
   ## Defaults to: '/tmp/thumbor/result_storage'
   #RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/result_storage'

   ## Indicates whether unsafe requests should also be stored in the Result Storage
   ## Defaults to: False
   #RESULT_STORAGE_STORES_UNSAFE = False

   ################################################################################


   ############################# Queued Redis Detector #############################

   ## Server host for the queued redis detector
   ## Defaults to: 'localhost'
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
   ## Defaults to: 'us-east-1'
   #SQS_QUEUE_REGION = 'us-east-1'

   ################################################################################


   #################################### Errors ####################################

   ## This configuration indicates whether thumbor should use a custom error
   ## handler.
   ## Defaults to: False
   #USE_CUSTOM_ERROR_HANDLING = False

   ## Error reporting module. Needs to contain a class called ErrorHandler with a
   ## handle_error(context, handler, exception) method.
   ## Defaults to: 'thumbor.error_handlers.sentry'
   #ERROR_HANDLER_MODULE = 'thumbor.error_handlers.sentry'

   ## File of error log as json
   ## Defaults to: None
   #ERROR_FILE_LOGGER = None

   ## File of error log name is parametrized with context attribute
   ## Defaults to: False
   #ERROR_FILE_NAME_USE_CONTEXT = False

   ################################################################################


   ############################### Errors - Sentry ################################

   ## Sentry thumbor project dsn. i.e.: http://5a63d58ae7b94f1dab3dee740b301d6a:73ee
   ## a45d3e8649239a973087e8f21f98@localhost:9000/2
   ## Defaults to: ''
   #SENTRY_DSN_URL = ''

   ## Sentry environment i.e.: staging
   ## Defaults to: None
   #SENTRY_ENVIRONMENT = None

   ################################################################################


   #################################### Server ####################################

   ## The amount of time to wait before shutting down the server, i.e. stop
   ## accepting requests.
   ## Defaults to: 0
   #MAX_WAIT_SECONDS_BEFORE_SERVER_SHUTDOWN = 0

   ## The amount of time to waut before shutting down all io, after the server has
   ## been stopped
   ## Defaults to: 0
   #MAX_WAIT_SECONDS_BEFORE_IO_SHUTDOWN = 0

   ################################################################################
