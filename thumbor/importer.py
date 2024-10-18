#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from importlib import import_module

from thumbor.utils import logger


def import_class(name, get_module=False):
    module_name = name if get_module else ".".join(name.split(".")[:-1])
    klass = name.split(".")[-1]

    module = import_module(module_name)
    return module if get_module else getattr(module, klass)


def noop(func):
    def noop_decorator(*args, **kw):
        return func(*args, **kw)  # pass through

    return noop_decorator


# Unfortunately this is a very useful class and rearchitecting it is going to be hard
# So while we agree that it has too many attributes, it will remain like that for now
class Importer:  # pylint: disable=too-many-instance-attributes
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.gif_engine = None
        self.loader = None
        self.url_signer = None
        self.upload_photo_storage = None
        self.storage = None
        self.metrics = None
        self.result_storage = None
        self.detectors = []
        self.filters = []
        self.optimizers = []
        self.handler_lists = []
        self.error_handler_module = None
        self.error_handler_class = None
        self.compatibility_legacy_loader = None
        self.compatibility_legacy_storage = None
        self.compatibility_legacy_result_storage = None

    @staticmethod
    def import_class(name, get_module=False, validate_fn=None):
        kls = import_class(name, get_module)
        if validate_fn is not None:
            validate_fn(kls)
        return kls

    def import_modules(self):
        if (
            self.config.COMPATIBILITY_LEGACY_LOADER
            or self.config.COMPATIBILITY_LEGACY_STORAGE
            or self.config.COMPATIBILITY_LEGACY_RESULT_STORAGE
        ):
            Importer.deprecated_monkey_patch_tornado_return_future()

        self.config.validates_presence_of(
            "ENGINE",
            "GIF_ENGINE",
            "LOADER",
            "STORAGE",
            "DETECTORS",
            "FILTERS",
            "URL_SIGNER",
            "METRICS",
            "HANDLER_LISTS",
        )

        self.import_item("ENGINE", "Engine")
        self.import_item("GIF_ENGINE", "Engine")
        self.import_item("LOADER")
        self.import_item("STORAGE", "Storage")
        self.import_item("METRICS", "Metrics")
        self.import_item("DETECTORS", "Detector", is_multiple=True)
        self.import_item(
            "FILTERS", "Filter", is_multiple=True, ignore_errors=True
        )
        self.import_item("HANDLER_LISTS", is_multiple=True)
        self.import_item("OPTIMIZERS", "Optimizer", is_multiple=True)
        self.import_item("URL_SIGNER", "UrlSigner")

        if self.config.RESULT_STORAGE:
            self.import_item("RESULT_STORAGE", "Storage")

        if self.config.UPLOAD_PHOTO_STORAGE:
            self.import_item("UPLOAD_PHOTO_STORAGE", "Storage")

        if self.config.USE_CUSTOM_ERROR_HANDLING:
            self.import_item("ERROR_HANDLER_MODULE", "ErrorHandler")
            self.error_handler_class = self.error_handler_module

        if self.config.COMPATIBILITY_LEGACY_LOADER:
            self.import_item("COMPATIBILITY_LEGACY_LOADER")

        if self.config.COMPATIBILITY_LEGACY_STORAGE:
            self.import_item("COMPATIBILITY_LEGACY_STORAGE", "Storage")

        if self.config.COMPATIBILITY_LEGACY_RESULT_STORAGE:
            self.import_item("COMPATIBILITY_LEGACY_RESULT_STORAGE", "Storage")

    @staticmethod
    def deprecated_monkey_patch_tornado_return_future():
        import tornado.concurrent  # pylint: disable=import-outside-toplevel

        if not hasattr(tornado.concurrent, "return_future"):
            setattr(tornado.concurrent, "return_future", noop)

    def import_item(  # pylint: disable=too-many-positional-arguments
        self,
        config_key=None,
        class_name=None,
        is_multiple=False,
        item_value=None,
        ignore_errors=False,
        validate_fn=None,
    ):
        if item_value is None:
            conf_value = getattr(self.config, config_key)
        else:
            conf_value = item_value

        if is_multiple:
            self.load_multiple_item(
                config_key,
                conf_value,
                class_name,
                ignore_errors,
                validate_fn,
            )
        else:
            if class_name is not None:
                module = self.import_class(f"{conf_value}.{class_name}")
            else:
                module = self.import_class(conf_value, get_module=True)
            setattr(self, config_key.lower(), module)

    def load_multiple_item(  # pylint: disable=too-many-positional-arguments
        self,
        config_key,
        conf_value,
        class_name,
        ignore_errors,
        validate_fn,
    ):
        modules = []
        if conf_value:
            for module_name in conf_value:
                try:
                    if class_name is not None:
                        if class_name == "*":
                            module = self.import_class(
                                module_name, validate_fn=validate_fn
                            )
                        else:
                            module = self.import_class(
                                f"{module_name}.{class_name}",
                                validate_fn=validate_fn,
                            )
                    else:
                        module = self.import_class(
                            module_name,
                            get_module=True,
                            validate_fn=validate_fn,
                        )
                    modules.append(module)
                except ImportError as error:
                    if ignore_errors:
                        logger.warning(
                            "Module %s could not be imported: %s",
                            module_name,
                            error,
                        )
                    else:
                        raise
        setattr(self, config_key.lower(), tuple(modules))
