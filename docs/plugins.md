# Plugins

With its pluggable architecture, Thumbor provides extension points for
storages, result storages, loaders, detectors, filters, engines, optimizers,
metrics, error handlers and handler lists.

If your plug-in is not listed here, please create an issue with the details and
we'll add it here.

```{important}
The projects listed here are maintained independently and may target different
Thumbor or Python versions. Before deploying one, verify its supported
versions, release status and configuration in the plugin's own documentation.
A listing on this page is not a compatibility guarantee.
```

Thumbor configuration values name importable Python modules. Depending on the
extension point, the module must expose the class expected by Thumbor:
`Storage`, `Engine`, `Optimizer`, `Detector`, `Filter`, `Metrics` or
`ErrorHandler`. Loader and handler-list entries are module-based interfaces.
See the corresponding customization guide for current method signatures.

Plugins may define configuration keys that are not part of Thumbor core. Those
keys are available to the plugin through `context.config`; keep their spelling
and Python value types exactly as documented by the plugin. Moving a list,
boolean, number, dictionary or `None` from `thumbor.conf` to the legacy
environment-variable interface changes it to a string.

## Defining plugin configuration

Plugin modules should register their defaults through `thumbor.config.Config`
when they are imported:

```python
from thumbor.config import Config


Config.define(
    "MY_PLUGIN_TIMEOUT",
    5,
    "Maximum time in seconds for my plugin operation",
    "My Plugin",
)
```

Always import `Config` from `thumbor.config`, not directly from `derpconf`.
Thumbor keeps the definition registry live, so a setting registered while a
configured plugin is imported becomes available to the already loaded config.
An explicit value from `thumbor.conf` continues to take precedence over the
plugin default:

```python
MY_PLUGIN_TIMEOUT = 10
LOADER = "my_plugin.loader"
```

The legacy Python loader also preserves uppercase plugin settings that have no
registered default. Registration is still recommended because it supplies a
default, description and group metadata. Plugin code can read the resolved
value through the configuration object it receives directly or through
`context.config`.

## Storages

### [thumbor_aws](https://github.com/thumbor-community/aws)

By [Thumbor Community](https://github.com/thumbor-community).

[Thumbor](https://github.com/thumbor/thumbor/wiki) is a smart imaging service.
It enables on-demand crop, resizing and flipping of images.

[AWS](https://aws.amazon.com/) is a cloud service, providing - among other
things - storage capabilities.

This module provides support for AWS S3 interconnection, as a loader, a storage
and/or a result storage.

- *URL:* <https://github.com/thumbor-community/aws>
- *Installing:* `pip install tc_aws`

For complete, version-specific configuration, use the documentation in the
plugin repository linked above.

### [thumbor_hbase](https://github.com/dhardy92/thumbor_hbase)

By [Damien Hardy](https://github.com/dhardy92).

[Thumbor](https://github.com/thumbor/thumbor/wiki) is a smart imaging service.
It enables on-demand crop, resizing and flipping of images.

[Hbase](https://hbase.apache.org/) is a column oriented database from the hadoop
ecosystem.

This module provide support for Hadoop Hbase as large auto replicant key/value
backend storage for images in Thumbor.

- *URL:* <https://github.com/dhardy92/thumbor_hbase>
- *Installing:* `pip install thumbor_hbase`

Using it is simple, just change your configuration in thumbor.conf:

```
HBASE_STORAGE_SERVER_HOST = "localhost"
HBASE_STORAGE_SERVER_PORT = 9000
HBASE_STORAGE_TABLE = "storage-table"
HBASE_STORAGE_FAMILY = "storage-family"
```

If you want to use thumbor_hbase for loading original images, change your
thumbor.conf to read:

```
LOADER = "thumbor_hbase.loader"
```

If you want to use thumbor_hbase for storage of original images, change your
thumbor.conf to read:

```
STORAGE = "thumbor_hbase.storage"
```

### [thumbor_mongodb](https://github.com/dhardy92/thumbor_mongodb)

By [Damien Hardy](https://github.com/dhardy92).

[Thumbor](https://github.com/thumbor/thumbor/wiki) is a smart imaging service.
It enables on-demand crop, resizing and flipping of images.

[MongoDB](http://www.mongodb.org/) is a document oriented NoSQL database.

This plugin for Thumbor is a loader that can reach images from a mongodb
collection based on its Object(\_id).

- *URL:* <https://github.com/dhardy92/thumbor_mongodb>
- *Installing:* `pip install thumbor_mongodb`

Using it is simple, just change your configuration in thumbor.conf:

```
LOADER = 'thumbor_mongodb.loader'
MONGO_LOADER_CNX_STRING = 'mongodb://mongodbserver01,mongodbserver02:27017'
MONGO_LOADER_SERVER_DB = 'thumbor'
MONGO_LOADER_SERVER_COLLECTION = 'images'
MONGO_LOADER_DOC_FIELD = 'content'
```

### [thumbor_riak](https://github.com/dhardy92/thumbor_riak)

By [Damien Hardy](https://github.com/dhardy92).

[Riak](http://basho.com/riak/) is a distributed document oriented database
implementing the consistent hashing algorithm from the Dynanmo publication by
Amazon.

This module provide support for Riak as a large auto replicant key/value backend
storage for images in Thumbor.

- *URL:* <https://github.com/dhardy92/thumbor_riak>
- *Installing:* `pip install thumbor_riak` (require thumbor)

Using it is simple, just change your configuration in thumbor.conf:

```
# Use riak for storage.
STORAGE = 'thumbor_riak.storage'

# Put the url for your riak install here
RIAK_STORAGE_BASEURL = "http://my-riak-install-base-url"
```

### [thumbor_rackspace](https://github.com/CodingNinja/thumbor_rackspace)

By [David Mann](https://github.com/CodingNinja).

This plugin allows users to store objects in the Rackspace cloud for result
storage.

- *URL:* <https://github.com/CodingNinja/thumbor_rackspace>
- *Installing:* `pip install thumbor_rackspace`

Using it is simple, just change your configuration in thumbor.conf:

```
# Use rackspace for result storage.
# For more information, see the result-storage page in thumbor's wiki.
RESULT_STORAGE = 'thumbor_rackspace.result_storages.cloudfile_storage'

# Pyrax Rackspace configuration file location
RACKSPACE_PYRAX_CFG = /var/thumbor/.pyrax.cfg

# Result Storage options
RACKSPACE_RESULT_STORAGE_EXPIRES = True # Set TTL on cloudfile objects
RACKSPACE_RESULT_STORAGES_CONTAINER = "cloudfile-container-name"
RACKSPACE_RESULT_STORAGES_CONTAINER_ROOT = "/"
```

### [thumbor_ceph](https://github.com/ksperis/thumbor_ceph)

By [Laurent Barbe](https://github.com/ksperis).

[Ceph](https://ceph.com/) a distributed object store designed to provide
excellent performance, reliability and scalability.

This module provide support for Ceph RADOS as backend storage for images.

- *URL:* <https://github.com/ksperis/thumbor_ceph>
- *Installing:* `apt-get install python-ceph && pip install thumbor_ceph`

Configuration in thumbor.conf:

```
################################# File Storage #################################
STORAGE = 'thumbor_ceph.storages.ceph_storage'
CEPH_STORAGE_POOL = 'thumbor'

#################################### Upload ####################################
UPLOAD_PHOTO_STORAGE = 'thumbor_ceph.storages.ceph_storage'

################################ Result Storage ################################
RESULT_STORAGE = 'thumbor_ceph.result_storages.ceph_storage'
CEPH_RESULT_STORAGE_POOL = 'thumbor'
```

For monitors and keys, the values ​​used are those defined in the configuration
file ceph.conf.

### [thumbor_spaces](https://github.com/siddhartham/thumbor_spaces)

By [Siddhartha Mukherjee](https://github.com/siddhartham).

This plugin allows users to store objects in the DigitalOcean Spaces for result
storage.

- *URL:* <https://github.com/siddhartham/thumbor_spaces>
- *Installing:* `pip install thumbor_spaces`

Using it is simple, just change your configuration in thumbor.conf:

```
# Use DigitalOcean Spaces for result storage.
# For more information, see the result-storage page in thumbor's wiki.
RESULT_STORAGE = 'thumbor_spaces.result_storages.spaces_storage'

SPACES_REGION='xxx'

SPACES_ENDPOINT='xxx'

SPACES_KEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

SPACES_SECRET='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

SPACES_BUCKET='your-bucket-name'
```

## Metrics

### [thumbor_prometheus](https://github.com/thumbor-community/prometheus)

By [Simon Effenberg](https://github.com/savar).

[Prometheus](https://prometheus.io/) a monitoring and alerting toolkit.

This module provide support for Prometheus as metrics collector.

- *URL:* <https://github.com/thumbor-community/prometheus>
- *Installing:* `pip install tc_prometheus`

Configuration in thumbor.conf:

```
############################### Extensibility ###############################
METRICS = 'tc_prometheus.metrics.prometheus_metrics'

# optional with defaults
PROMETHEUS_SCRAPE_PORT = 8000 # Port the prometheus client should listen on
```

## Extensions

### [thumborshortener](https://github.com/thumbor-community/shortener)

By [Thumbor Community](https://github.com/thumbor-community).

[Thumbor](https://github.com/thumbor/thumbor/wiki) is a smart imaging service.
It enables on-demand crop, resizing and flipping of images.

This module provides URL shortening capabilities for Thumbor. It will create an
API that can shorten a thumbor URL, and then routing capabilities to reroute the
shortened URL to the correct image.

The shortened URL / real URL mapping is stored within redis.

- *URL:* <https://github.com/thumbor-community/shortener>
- *Installing:* `pip install tc_shortener`

To get exhaustive details about configuration options & setting it up, go to the
[plugin documentation](http://thumbor-shortener.readthedocs.io/).

## Engines

### [thumbor-video-engine](https://github.com/theatlantic/thumbor-video-engine)

By [The Atlantic](https://github.com/theatlantic).

This engine extends thumbor so that it can read, crop, and transcode audio-less
video files using FFmpeg. It supports input and output of animated GIF, animated
WebP, WebM (VP9) video, and MP4 (H.264 and H.265).

- *URL:* <https://github.com/theatlantic/thumbor-video-engine>
- *Installing:* `pip install thumbor-video-engine`

Configuration in thumbor.conf:

```
ENGINE = 'thumbor_video_engine.engines.video'
FILTERS = [
    # Enables transcoding between video formats (in addition to the image
    # formats already supported by thumbor.filters.format)
    'thumbor_video_engine.filters.format',
    # Allows outputting a still frame from a video as an image
    'thumbor_video_engine.filters.still',
]

# optional, if you are already using a custom image engine
IMAGING_ENGINE = 'opencv_engine'
```

For a full list of configuration options and filters, read
[the project's documentation](https://thumbor-video-engine.readthedocs.io/).
