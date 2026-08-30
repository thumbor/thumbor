# Configuration

thumbor's configuration file is just a regular python script that gets loaded by
thumbor.

When no configuration path is provided, thumbor looks for `thumbor.conf` in
this order:

1. the current working directory;
2. the current user's home directory;
3. `/etc`;
4. the installed `thumbor` package directory.

The first file found is loaded. Pass `-c` or `--conf` to load a specific file
instead. An explicit path is used as provided; thumbor does not expand `~` in
that argument. Relative explicit paths are resolved from the current working
directory.

To generate a commented template for the installed version, run:

```bash
thumbor-config > ./thumbor.conf
```

This command writes to standard output. Shell redirection creates or replaces
the destination file; it does not merge with an existing configuration.

## Override configuration through environment variables

Environment overrides are disabled by default. To enable the legacy derpconf
environment lookup, pass a value to `--use-environment`, for example:

```bash
SECURITY_KEY=my-secret-key thumbor --use-environment=true
```

The environment variable name must exactly match the configuration key; there
is no prefix. Environment values are returned as strings and override values
loaded from `thumbor.conf` whenever that key is read. Consequently, this mode
is safe only for string-valued settings. Boolean, integer, list, dictionary and
other typed settings should remain in `thumbor.conf`.

`--use-environment` currently requires a value. A bare `--use-environment`
argument is not accepted.

## Extensibility Section

### LOADER

The loader is responsible for retrieving the source image that thumbor will work
with. This configuration defines the module that thumbor will use for it. **This
must be a full namespace module (a.k.a. python has to be able to \*import\*
it).**

```python
LOADER = 'thumbor.loaders.http_loader'
```

### STORAGE

The storage is responsible for storing the source image bytes and related
metadata (face-detection, encryption and such) so that we don't keep loading it
every time. **This must be a full namespace module (a.k.a. python has to be able
to \*import\* it).**

```python
STORAGE = 'thumbor.storages.file_storage'
```

### MIXED_STORAGE_FILE_STORAGE

If you are using thumbor's mixed storage (`thumbor.storages.mixed_storage`),
this is where you specify the storage that will be used to store images. **This
must be a full namespace module (a.k.a. python has to be able to \*import\*
it).**

```python
MIXED_STORAGE_FILE_STORAGE = 'thumbor.storages.file_storage'
```

### MIXED_STORAGE_CRYPTO_STORAGE

If you are using thumbor's mixed storage (`thumbor.storages.mixed_storage`),
this is where you specify the storage that will be used to store cryptography
information. **This must be a full namespace module (a.k.a. python has to be
able to \*import\* it).**

```python
MIXED_STORAGE_CRYPTO_STORAGE = 'thumbor.storages.file_storage'
```

### MIXED_STORAGE_DETECTOR_STORAGE

If you are using thumbor's mixed storage (`thumbor.storages.mixed_storage`),
this is where you specify the storage that will be used to store facial and
feature detection results. **This must be a full namespace module (a.k.a. python
has to be able to \*import\* it)**.

```python
MIXED_STORAGE_DETECTOR_STORAGE = 'thumbor.storages.file_storage'
```

### RESULT_STORAGE

The result storage is responsible for storing the resulting image with the
specified parameters (think of it as a cache), so that we don't keep processing
it every time a request comes in. **This must be a full namespace module (a.k.a.
python has to be able to \*import\* it).**

```python
RESULT_STORAGE = 'thumbor.result_storages.file_storage'
```

### ENGINE

The engine is responsible for transforming the image. **This must be a full
namespace module (a.k.a. python has to be able to \*import\* it).**

Currently, thumbor ships with only the `thumbor.engines.pil` imaging engine. A
few years ago we conducted a comparison between the engines and there was no
clear winner. Given PIL was the engine we were using at the time, we decided to
stick with it. Other open source engines exist and you can find more about them
in the plug-in section of the docs.

```python
ENGINE = 'thumbor.engines.pil'
```

### URL_SIGNER

The url signer is responsible for validation and signing of requests to prevent
url tampering, which could lead to denial of service (example: filling the
result_storage by specifying a different size). **This must be a full namespace
module (a.k.a. python has to be able to \*import\* it).**

```python
URL_SIGNER = 'libthumbor.url_signers.base64_hmac_sha1'
```

## Filters Section

In order to specify the filters that thumbor will use, you need a configuration
key called `FILTERS`. This is a regular python list with the full names (names
that python can import) of the filter modules you want to use.

i.e.:

```python
FILTERS = [
    'thumbor.filters.brightness',
    'thumbor.filters.contrast',
    'thumbor.filters.rgb',
    'thumbor.filters.round_corner',
    'thumbor.filters.quality',
    'thumbor.filters.noise',
    'thumbor.filters.watermark',
]
```

## Metadata Section

### META_CALLBACK_NAME

If you want thumbor to use JSONP for image metadata instead of using JSON, just
set this variable to the callback name you want.

```python
META_CALLBACK_NAME = 'thumbor_callback'  # Or None for no callback
```

## Face and Feature Detection Section

### DETECTORS

This options specifies the detectors that should run the image to check for
focal points.

i.e.:

```python
 DETECTORS = [
   'thumbor.detectors.face_detector',
   'thumbor.detectors.feature_detector'
]
```

### Cascade Files

This option specifies the cascade (XML) file paths to train openCV to find faces
or other objects.

```python
## The cascade file that opencv will use to detect faces.
FACE_DETECTOR_CASCADE_FILE = 'haarcascade_frontalface_alt.xml'

## The cascade file that opencv will use to detect glasses.
GLASSES_DETECTOR_CASCADE_FILE = 'haarcascade_eye_tree_eyeglasses.xml'

## The cascade file that opencv will use to detect profile faces.
PROFILE_DETECTOR_CASCADE_FILE = 'haarcascade_profileface.xml'
```

## Imaging Section

### ALLOWED_SOURCES

This configuration defines the source of the images that thumbor will load. This
is only used in the HttpLoader (check the LOADER configuration above).

Plain string entries are matched literally against the request hostname. Dots
are not wildcards.

```python
ALLOWED_SOURCES = ['s.glbimg.com']
```

Regex-like string entries are accepted only for backward compatibility and will
log a warning. For wildcard or regular expression entries, use compiled regular
expression objects. Compiled patterns are matched against the full normalized
image URL.

```python
import re

ALLOWED_SOURCES = [
    re.compile(r'https?://[^/]+\.globo\.com/.*'),
    re.compile(r'https?://[^/]+\.glbimg\.com/.*'),
]
```

This is to get any images that are in `*.globo.com` or `*.glbimg.com` and fail
with any other domains.

### ACCESS_CONTROL_ALLOW_ORIGIN_HEADER

This allows to send the ACCESS_CONTROL_ALLOW_ORIGIN header. For example, if you
want to tell the browser to allow code from any origin to access your thumbor
resources:

```python
ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = '*'
```

If you want restrict access to a certain resource:

```python
ACCESS_CONTROL_ALLOW_ORIGIN_HEADER = 'https://www.example.com'
```

Not set by default.

### MAX_WIDTH and MAX_HEIGHT

These define the box that the resulting image for thumbor must fit-in. This
means that no image that thumbor generates will have a width larger than
MAX_WIDTH or height larger than MAX_HEIGHT. It defaults to 0, which means there
is not limit. If the original image is larger than MAX_WIDTH x MAX_HEIGHT, it is
proportionally resized to MAX_WIDTH x MAX_HEIGHT.

```python
MAX_WIDTH = 1200
MAX_HEIGHT = 800
```

### MIN_WIDTH and MIN_HEIGHT

These define the box that the resulting image for thumbor must fit-in. This
means that no image that thumbor generates will have a width smaller than
MIN_WIDTH or height smaller than MIN_HEIGHT. It defaults to 1. If the original
image is smaller than MIN_WIDTH x MIN_HEIGHT, it is proportionally resized to
MIN_WIDTH x MIN_HEIGHT.

```python
MIN_WIDTH = 1
MIN_HEIGHT = 1
```

### QUALITY

This option defines the quality that JPEG images will be generated with. It
defaults to 80.

```python
QUALITY = 90
```

### MAX_AGE

This option defines the number of seconds that images should remain in the
browser's cache. It relates directly with the Expires and Cache-Control headers.

```python
MAX_AGE = 24 * 60 * 60  # A day of caching
```

### MAX_AGE_TEMP_IMAGE

When an image has some error in its detection or it has deferred queueing, it's
convenient to set a much lower expiration time for the image cache. This way the
browser will request the proper image faster.

This option defines the number of seconds that images in this scenario should
remain in the browser's cache. It relates directly with the Expires and
Cache-Control headers.

```python
MAX_AGE_TEMP_IMAGE = 60  # A minute of caching
```

### RESPECT_ORIENTATION

If this option is set to True, thumbor will reorient the image according to it's
EXIF Orientation tag (if one can be found). This options defaults to False.

The operations performed in the image are as follow (considering the value of
the Orientation EXIF tag):

1. Nothing
1. Flips the image horizontally
1. Rotates the image 180 degrees
1. Flips the image vertically
1. Flips the image vertically and rotates 270 degrees
1. Rotates the image 270 degrees
1. Flips the image horizontally and rotates 270 degrees
1. Rotates the image 90 degrees

```python
RESPECT_ORIENTATION = False
```

### ALLOW_ANIMATED_GIFS

This option indicates whether animated gifs should be supported.

```python
ALLOW_ANIMATED_GIFS = True
```

### USE_GIFSICLE_ENGINE

This option indicates whether [gifsicle](http://www.lcdf.org/gifsicle/man.html)
should be used for all gif images, instead of the actual imaging engine. This
defaults to False.

**When using gifsicle thumbor will generate proper animated gifs, as well as
static gifs with the smallest possible size.**

```python
USE_GIFSICLE_ENGINE = True
```

WARNING: When using gifsicle engine, filters will be skipped, except for
`cover()` filter. thumbor will not do smart cropping as well.

### AUTO\_\*

These configurations indicates that thumbor will try to automatically convert
the image format to a lighter image format, according to this compression order:
`WEBP, AVIF, JPG, HEIF, PNG` — from highest (`WEBP`) to lowest (`PNG`) priority.

#### AUTO_WEBP

This option indicates whether thumbor should send WebP images automatically if
the request comes with an "Accept" header that specifies that the browser
supports "image/webp".

```python
AUTO_WEBP = True
```

#### AUTO_AVIF

This option indicates whether thumbor should send Avif images automatically if
the request comes with an "Accept" header that specifies that the browser
supports "image/avif" and pillow-avif-plugin is enabled.

```python
AUTO_AVIF = True
```

#### AUTO_PNG_TO_JPG

This option indicates whether thumbor should transform PNG images automatically
to JPEG. If the image is a PNG without transparency and the numpy dependency is
installed, thumbor will transform from png to jpeg. In the most of cases the
image size will decrease.

WARNING: Depending on case, this is not a good deal. This transformation maybe
causes distortions or the size of image can increase. Images with texts, for
example, the result image maybe will be distorted. Dark images, for example, the
size of result image maybe will be bigger. You have to evaluate the majority of
your use cases to take a decision about the usage of this conf.

This conversion remains independent of `AUTO_IMAGE_FORMAT_PREFERENCE`. When a
preference list is configured and none of its entries can be used, thumbor still
applies `AUTO_PNG_TO_JPG` as a fallback. The `autojpg()` filter enables or
disables this fallback for an individual request; it does not enable or disable
a `jpg` entry in the preference list.

```python
AUTO_PNG_TO_JPG = True
```

#### AUTO_JPG

This option indicates whether thumbor should send JPG images automatically if
the request comes with an "Accept" header that specifies that the browser
supports `*/*`, `image/jpg` or `image/jpeg`.

```python
AUTO_JPG = True
```

#### AUTO_PNG

This option indicates whether thumbor should send PNG images automatically if
the request comes with an "Accept" header that specifies that the browser
supports "image/png".

```python
AUTO_PNG = True
```

#### AUTO_HEIF

This option indicates whether thumbor should send Heif images automatically if
the request comes with an "Accept" header that specifies that the browser
supports "image/heif" and pillow-heif is enabled.

```python
AUTO_HEIF = True
```

#### AUTO_IMAGE_FORMAT_PREFERENCE

This option defines the order in which thumbor attempts automatic output
formats. The valid tokens are `webp`, `avif`, `jpg`, `heif` and `png`. Values
are stripped of surrounding whitespace and converted to lowercase. Duplicate
values after the first occurrence, non-string values and unknown tokens are
ignored.

For each entry, thumbor checks the request's `Accept` header and the current
engine's capabilities, then selects the first eligible format. AVIF and HEIF
therefore require their respective engine support, JPEG is not selected for an
image with transparency, and preference entries are not selected for multi-image
input. Media types are matched case-insensitively, and an entry with an explicit
quality value of `q=0` is not eligible. `image/*` applies to all supported image
formats, while the less specific `*/*` retains the legacy behavior of enabling
JPEG only. If no entry is eligible, thumbor preserves the engine's output
format, except for the independent `AUTO_PNG_TO_JPG` fallback described above.

A preference list containing at least one valid entry overrides `AUTO_WEBP`,
`AUTO_AVIF`, `AUTO_JPG`, `AUTO_PNG` and `AUTO_HEIF`. If any entries are invalid,
thumbor logs one warning listing the ignored values. If every entry is invalid,
thumbor treats the preference as empty. An empty preference uses the individual
settings in their legacy order: `webp`, `avif`, `jpg`, `heif`, then `png`.

```python
# Prioritize AVIF over WebP.
AUTO_IMAGE_FORMAT_PREFERENCE = ["avif", "webp", "jpg", "png", "heif"]

# Or prioritize JPEG for workloads where that is preferable.
AUTO_IMAGE_FORMAT_PREFERENCE = ["jpg", "webp", "avif", "png", "heif"]
```

The result-storage cache key must vary with the active formats accepted by the
request. The built-in file result storage does this automatically and uses an
isolated namespace whenever a preference, `AUTO_AVIF`, `AUTO_JPG`, `AUTO_HEIF`,
`AUTO_PNG` or `AUTO_PNG_TO_JPG` is active. It migrates legacy entries only for
configurations where the old `default` or WebP namespace is unambiguous. Custom
result storages must use
`thumbor.auto_image_format.get_auto_image_format_cache_key` as described in
{doc}`custom_result_storages`. When enabling or reordering this setting, do not
migrate a legacy cached object into a new format namespace unless its content
type is verified; a cache purge is the safest upgrade path for storages that
cannot isolate the old entries.

This namespace change also applies on upgrade when the preference remains empty
but `AUTO_AVIF`, `AUTO_JPG`, `AUTO_HEIF`, `AUTO_PNG` or `AUTO_PNG_TO_JPG` is
already enabled. Existing generated images in the legacy `default` namespace are
deliberately treated as cache misses and regenerated. Plan for a temporarily
cold cache, pre-warm it or use a gradual rollout if the additional origin and
processing load would be significant. Legacy files are not removed
automatically, so account for their disk usage until they are cleaned up
separately. An `AUTO_WEBP`-only configuration keeps its existing cache
namespace.

The default is an empty list, which retains the individual `AUTO_*` settings.

```python
# Use individual AUTO_* settings (default behavior).
AUTO_IMAGE_FORMAT_PREFERENCE = []
```

## Queueing - Redis Single Node

### REDIS_QUEUE_MODE

Redis operation mode 'single_node' or 'sentinel'

```python
REDIS_QUEUE_MODE = 'single_node'
```

### REDIS_QUEUE_SERVER_HOST

Server host for the queued redis detector.

```python
REDIS_QUEUE_SERVER_HOST = 'localhost'
```

### REDIS_QUEUE_SERVER_PORT

Server port for the queued redis detector.

```python
REDIS_QUEUE_SERVER_PORT = 6379
```

### REDIS_QUEUE_SERVER_DB

Server database index for the queued redis detector

```python
REDIS_QUEUE_SERVER_DB = 0
```

### REDIS_QUEUE_SERVER_PASSWORD

Server password for the queued redis detector

```python
REDIS_QUEUE_SERVER_PASSWORD = None
```

## Queueing - Redis Sentinel

### REDIS_QUEUE_MODE

Redis operation mode 'single_node' or 'sentinel'

```python
REDIS_QUEUE_MODE = 'sentinel'
```

### REDIS_QUEUE_SENTINEL_INSTANCES

Sentinel server instances for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_INSTANCES = 'localhost:23679,localhost:23680'
```

### REDIS_QUEUE_SENTINEL_PASSWORD

Sentinel server password for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_PASSWORD = None
```

### REDIS_QUEUE_SENTINEL_MASTER_INSTANCE

Sentinel server master instance for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_MASTER_INSTANCE = 'masterinstance'
```

### REDIS_QUEUE_SENTINEL_MASTER_PASSWORD

Sentinel server master password for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_MASTER_PASSWORD = None
```

### REDIS_QUEUE_SENTINEL_MASTER_DB

Sentinel server master database index for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_MASTER_DB = 0
```

### REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT

Sentinel server socket timeout for the queued redis detector.

```python
REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT = 10.0
```

## Queueing - Amazon SQS

This queue will be removed in an upcoming release in favor of the open source
AWS plug-ins for thumbor.

### SQS_QUEUE_KEY_ID

Amazon AWS key id.

```python
SQS_QUEUE_KEY_ID = None
```

### SQS_QUEUE_KEY_SECRET

Amazon AWS key secret.

```python
SQS_QUEUE_KEY_SECRET = None
```

### SQS_QUEUE_REGION

Amazon AWS SQS region.

```python
SQS_QUEUE_REGION = 'us-east-1'
```

## Security Section

### SECURITY_KEY

This option specifies the security key that thumbor uses to sign secure URLs.

```python
SECURITY_KEY = "replace-this-with-a-secret-key"
```

Do not use the example value in production.

### ALLOW_UNSAFE_URL

This option specifies that the /unsafe url should be available in this thumbor
instance. It is boolean (True or False).

```{warning}
It is **STRONGLY** recommended that you turn off this flag in production
environments, as this can lead to DDoS attacks against thumbor.
```

```python
ALLOW_UNSAFE_URL = False
```

## Loader Options Section

### FILE_LOADER_ROOT_PATH

In case you are using thumbor's built-in file loader, this is the option that
allows you to specify where to find the images.

```python
FILE_LOADER_ROOT_PATH = "/home/thumbor/images"
```

### HTTP_LOADER_DEFAULT_USER_AGENT

This option allows users to specify the default user-agent that thumbor will
send when requesting images with the HTTP Loader. Defaults to 'thumbor/' (like
thumbor/7.0.0).

```python
HTTP_LOADER_DEFAULT_USER_AGENT = 'thumbor/7.0.0'
```

### HTTP_LOADER_FORWARD_USER_AGENT

This option tells thumbor to forward the request user agent when requesting
images using the HTTP Loader. Defaults to False.

```python
HTTP_LOADER_FORWARD_USER_AGENT = False
```

## Storage Options Section

### STORAGE_EXPIRATION_SECONDS

This options specifies the default expiration time in seconds for the storage.

```python
STORAGE_EXPIRATION_SECONDS = 60  # 1 minute
```

### STORES_CRYPTO_KEY_FOR_EACH_IMAGE

This option specifies whether thumbor should store the key for each image (thus
allowing the image to be found even if the security key changes). This is a
boolean flag (True or False).

```{warning}
If this flag is set to False, it essentially means that whenever you change
the security key, for whatever reason, you just invalidated every single image
that's been generated before.

That may be ok if you have another service fetching stored images instead of
allowing thumbor to do it (as many of thumbor users do).
```

```python
STORES_CRYPTO_KEY_FOR_EACH_IMAGE = True
```

## File Storage Section

### FILE_STORAGE_ROOT_PATH

In case you are using thumbor's built-in file storage, this is the option that
allows you to specify where to save the images.

```python
FILE_STORAGE_ROOT_PATH = '/home/thumbor/storage'
```

## Result Storage Section

### RESULT_STORAGE_EXPIRATION_SECONDS

Expiration in seconds of generated images in the result storage.

```python
RESULT_STORAGE_EXPIRATION_SECONDS = 0
```

### RESULT_STORAGE_FILE_STORAGE_ROOT_PATH

Path where the Result storage will store generated images.

```python
RESULT_STORAGE_FILE_STORAGE_ROOT_PATH = '/tmp/thumbor/result_storage'
```

### RESULT_STORAGE_STORES_UNSAFE

Indicates whether unsafe requests should also be stored in the Result Storage.

```python
RESULT_STORAGE_STORES_UNSAFE = False
```

## Healthcheck

### HEALTHCHECK_ROUTE

The URL path to a healthcheck. This will return a 200 and the text 'WORKING'.

```python
HEALTHCHECK_ROUTE = '/status'
```

Will put the healthcheck response on `http://host:port/status`

The default route is `/healthcheck`.

## Logging

### THUMBOR_LOG_FORMAT

This option specifies the format to be used by logging messages sent from
thumbor.

```python
THUMBOR_LOG_FORMAT = '%(asctime)s %(name)s:%(levelname)s %(message)s'
```

### THUMBOR_LOG_DATE_FORMAT

This option specifies the date format to be used by logging messages sent from
thumbor.

```python
THUMBOR_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
```

## Error Handling

### USE_CUSTOM_ERROR_HANDLING

This configuration indicates whether thumbor should use a custom error handler.

```python
USE_CUSTOM_ERROR_HANDLING = False
```

### ERROR_HANDLER_MODULE

Error reporting module. Needs to contain a class called ErrorHandler with a
handle_error(context, handler, exception) method.

```python
ERROR_HANDLER_MODULE = 'thumbor.error_handlers.sentry'
```

## Error Handling - Sentry

### SENTRY_DSN_URL

Sentry thumbor project DSN, for example:
`http://user:password@localhost:9000/2`.

```python
SENTRY_DSN_URL = ''
```

### SENTRY_ENVIRONMENT

Sentry thumbor environment.

```python
SENTRY_ENVIRONMENT = 'staging'
```

## Upload

### UPLOAD_MAX_SIZE

Max size in bytes for images uploaded to thumbor.

```python
UPLOAD_MAX_SIZE = 0
```

### UPLOAD_ENABLED

Indicates whether thumbor should enable File uploads.

```python
UPLOAD_ENABLED = False
```

### UPLOAD_PHOTO_STORAGE

The type of storage to store uploaded images with.

```python
UPLOAD_PHOTO_STORAGE = 'thumbor.storages.file_storage'
```

### UPLOAD_DELETE_ALLOWED

Indicates whether image deletion should be allowed.

```python
UPLOAD_DELETE_ALLOWED = False
```

### UPLOAD_PUT_ALLOWED

Indicates whether image overwrite should be allowed.

```python
UPLOAD_PUT_ALLOWED = False
```

### UPLOAD_DEFAULT_FILENAME

Default filename for image uploaded.

```python
UPLOAD_DEFAULT_FILENAME = 'image'
```

### GC_INTERVAL

Set manual garbage collection interval in seconds. Defaults to None (no manual
garbage collection). Try this if your thumbor is running out of memory. May
cause an increase in CPU load.

```python
GC_INTERVAL = 60
```

## Generate a configuration template

Generate the configuration template for the installed thumbor version with:

```bash
thumbor-config > ./thumbor.conf
```

The generated file is the authoritative list of built-in settings, defaults,
aliases and descriptions for that installed version. Keep custom Python code,
plugin settings and local overrides in your own `thumbor.conf`; regenerating
the template overwrites the destination selected by shell redirection.
