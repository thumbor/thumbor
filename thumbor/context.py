#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, exists

from thumbor.filters import FiltersFactory
from thumbor.metrics.logger_metrics import Metrics
from thumbor.threadpool import ThreadPool


# Same logic as Importer. This class is very useful and will remain like so for now
class Context:  # pylint: disable=too-many-instance-attributes
    """
    Class responsible for containing:
    * Server Configuration Parameters (port, ip, key, etc);
    * Configurations read from config file (or defaults);
    * Importer with imported modules (engine, filters, detectors, etc);
    * Request Parameters (width, height, smart, meta, etc).

    Each instance of this class MUST be unique per request.
    This class should not be cached in the server.
    """

    def __init__(
        self, server=None, config=None, importer=None, request_handler=None
    ):
        self.server = server
        self.config = config

        if importer:
            self.modules = ContextImporter(self, importer)

            if importer.metrics:
                self.metrics = importer.metrics(config)
            else:
                self.metrics = Metrics(config)
        else:
            self.modules = None
            self.metrics = Metrics(config)

        self.app_class = "thumbor.app.ThumborServiceApp"

        if hasattr(self.config, "APP_CLASS"):
            self.app_class = self.config.APP_CLASS

        if (
            hasattr(self.server, "app_class")
            and self.server.app_class != "thumbor.app.ThumborServiceApp"
        ):
            self.app_class = self.server.app_class

        self.filters_factory = FiltersFactory(
            self.modules.filters if self.modules else []
        )
        self.request_handler = request_handler
        self.thread_pool = ThreadPool.instance(
            getattr(config, "ENGINE_THREADPOOL_SIZE", 0)
        )
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exception_type, value, traceback):
        if self.modules:
            self.modules.cleanup()

        self.thread_pool.cleanup()


class ServerParameters:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        port,
        ip,  # pylint: disable=invalid-name
        config_path,
        keyfile,
        log_level,
        app_class,
        debug=False,
        fd=None,  # pylint: disable=invalid-name
        gifsicle_path=None,
        use_environment=False,
        processes=1,
    ):
        self.port = port
        self.ip = (  # Other people may depend on this pylint: disable=invalid-name
            ip
        )
        self.config_path = config_path
        self.keyfile = keyfile
        self.log_level = log_level
        self.app_class = app_class
        self.debug = debug
        self._security_key = None
        self.load_security_key()
        self.fd = (  # Other people may depend on this pylint: disable=invalid-name
            fd
        )
        self.gifsicle_path = gifsicle_path
        self.use_environment = use_environment
        self.processes = processes

    @property
    def security_key(self):
        return self._security_key

    @security_key.setter
    def security_key(self, key):
        self._security_key = key

    def load_security_key(self):
        if not self.keyfile:
            return

        path = abspath(self.keyfile)

        if not exists(path):
            raise ValueError(
                (
                    f"Could not find security key file at {path}. "
                    "Please verify the keypath argument."
                )
            )

        with open(path, "rb") as security_key_file:
            security_key = security_key_file.read().strip()

        self.security_key = security_key


class RequestParameters:  # pylint: disable=too-few-public-methods,too-many-instance-attributes,too-many-locals
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        debug=False,
        meta=False,
        trim=None,
        crop_left=None,
        crop_top=None,
        crop_right=None,
        crop_bottom=None,
        crop=None,
        adaptive=False,
        full=False,
        fit_in=False,
        stretch=False,
        width=0,
        height=0,
        horizontal_flip=False,
        vertical_flip=False,
        halign="center",
        valign="middle",
        filters=None,
        smart=False,
        quality=80,
        image=None,
        url=None,
        extension=None,  # pylint: disable=unused-argument
        buffer=None,  # pylint: disable=unused-argument
        focal_points=None,
        unsafe=False,
        hash=None,  # pylint: disable=unused-argument,redefined-builtin
        accepts_webp=False,
        request=None,
        max_age=None,
        auto_png_to_jpg=None,
    ):
        self.debug = bool(debug)
        self.meta = bool(meta)
        self.trim = trim

        if trim is not None:
            trim_parts = trim.split(":")
            self.trim_pos = (
                trim_parts[1] if len(trim_parts) > 1 else "top-left"
            )
            self.trim_tolerance = (
                int(trim_parts[2]) if len(trim_parts) > 2 else 0
            )

        if crop is not None:
            self.crop = {k: self.int_or_0(v) for k, v in crop.items()}
        else:
            self.crop = {
                "left": self.int_or_0(crop_left),
                "right": self.int_or_0(crop_right),
                "top": self.int_or_0(crop_top),
                "bottom": self.int_or_0(crop_bottom),
            }

        self.should_crop = (
            self.crop["left"] > 0
            or self.crop["top"] > 0
            or self.crop["right"] > 0
            or self.crop["bottom"] > 0
        )

        self.adaptive = bool(adaptive)
        self.full = bool(full)
        self.fit_in = bool(fit_in)
        self.stretch = bool(stretch)

        self.width = "orig" if width == "orig" else self.int_or_0(width)
        self.height = "orig" if height == "orig" else self.int_or_0(height)
        self.horizontal_flip = bool(horizontal_flip)
        self.vertical_flip = bool(vertical_flip)
        self.halign = halign or "center"
        self.valign = valign or "middle"
        self.smart = bool(smart)

        if filters is None:
            filters = []

        self.filters = filters
        self.image_url = image
        self.url = url
        self.detection_error = None
        self.quality = quality
        self.buffer = None

        if focal_points is None:
            focal_points = []

        self.focal_points = focal_points
        self.hash = hash
        self.prevent_result_storage = False
        self.unsafe = unsafe == "unsafe" or unsafe is True
        self.format = None
        self.accepts_webp = accepts_webp
        self.max_bytes = None
        self.max_age = max_age
        self.auto_png_to_jpg = auto_png_to_jpg
        self.headers = None

        if request:
            self.url = request.path
            self.accepts_webp = "image/webp" in request.headers.get(
                "Accept", ""
            )
            if request.headers:
                self.headers = request.headers

    @staticmethod
    def int_or_0(value):
        return 0 if value is None else int(value)


class ContextImporter:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, context, importer):
        self.context = context
        self.importer = importer

        self.engine = None

        if importer.engine:
            self.engine = importer.engine(context)

        self.gif_engine = None

        if importer.gif_engine:
            self.gif_engine = importer.gif_engine(context)

        self.storage = None

        if importer.storage:
            self.storage = importer.storage(context)

        self.result_storage = None

        if importer.result_storage:
            self.result_storage = importer.result_storage(context)

        self.upload_photo_storage = None

        if importer.upload_photo_storage:
            self.upload_photo_storage = importer.upload_photo_storage(context)

        self.loader = importer.loader
        self.detectors = importer.detectors
        self.filters = importer.filters
        self.optimizers = importer.optimizers
        self.url_signer = importer.url_signer

        self.compatibility_legacy_loader = importer.compatibility_legacy_loader

        self.compatibility_legacy_storage = None

        if importer.compatibility_legacy_storage is not None:
            self.compatibility_legacy_storage = (
                importer.compatibility_legacy_storage(context)
            )

        self.compatibility_legacy_result_storage = None

        if importer.compatibility_legacy_result_storage is not None:
            self.compatibility_legacy_result_storage = (
                importer.compatibility_legacy_result_storage(context)
            )

    def cleanup(self):
        if self.engine:
            self.engine.cleanup()
