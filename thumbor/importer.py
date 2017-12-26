#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

'Imports dynamic thumbor modules'

from functools import reduce

from thumbor.utils import logger


def import_class(name, get_module=False):
    'Imports a class from a module'
    module_name = name if get_module else '.'.join(name.split('.')[:-1])
    klass = name.split('.')[-1]

    module = __import__(name) if get_module else __import__(module_name)
    if '.' in module_name:
        module = reduce(getattr, module_name.split('.')[1:], module)

    return module if get_module else getattr(module, klass)


class Importer:  # pylint: disable=too-many-instance-attributes
    'Importer class responsible for dependency injection in thumbor'

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
        self.error_handler_class = None
        self.error_handler_module = None
        self.blueprints = []

    def import_class(self, name, get_module=False):  # pylint: disable=no-self-use
        '''
        Imports a class. This method is a simple
        redirection to allow it to be overriden.
        '''
        return import_class(name, get_module)

    def import_modules(self):
        'Imports all modules in config'
        self.config.validates_presence_of('ENGINE', 'GIF_ENGINE', 'LOADER',
                                          'STORAGE', 'DETECTORS', 'FILTERS',
                                          'URL_SIGNER', 'METRICS', 'BLUEPRINTS')

        self.import_item('ENGINE', 'Engine')
        self.import_item('GIF_ENGINE', 'Engine')
        self.import_item('LOADER')
        self.import_item('STORAGE', 'Storage')
        self.import_item('METRICS', 'Metrics')
        self.import_item('DETECTORS', 'Detector', is_multiple=True)
        self.import_item('BLUEPRINTS', is_multiple=True)

        self.import_item(
            'FILTERS', 'Filter', is_multiple=True, ignore_errors=True)
        self.import_item('OPTIMIZERS', 'Optimizer', is_multiple=True)
        self.import_item('URL_SIGNER', 'UrlSigner')

        if self.config.RESULT_STORAGE:
            self.import_item('RESULT_STORAGE', 'Storage')

        if self.config.UPLOAD_PHOTO_STORAGE:
            self.import_item('UPLOAD_PHOTO_STORAGE', 'Storage')

        if self.config.USE_CUSTOM_ERROR_HANDLING:
            self.import_item('ERROR_HANDLER_MODULE', 'ErrorHandler')
            self.error_handler_class = self.error_handler_module

    def import_item(  # pylint: disable=too-many-arguments
            self,
            config_key=None,
            class_name=None,
            is_multiple=False,
            item_value=None,
            ignore_errors=False):
        'Imports an item from configuration'

        if item_value is None:
            conf_value = getattr(self.config, config_key)
        else:
            conf_value = item_value

        if is_multiple:
            modules = self.__import_multiple(conf_value, class_name,
                                             ignore_errors)
            setattr(self, config_key.lower(), tuple(modules))
        else:
            if class_name is not None:
                module = self.import_class('%s.%s' % (conf_value, class_name))
            else:
                module = self.import_class(conf_value, get_module=True)
            setattr(self, config_key.lower(), module)

    def __import_multiple(self, conf_value, class_name, ignore_errors):
        modules = []
        if conf_value:
            for module_name in conf_value:
                try:
                    if class_name is not None:
                        module = self.import_class('%s.%s' % (module_name,
                                                              class_name))
                    else:
                        module = self.import_class(module_name, get_module=True)
                    modules.append(module)
                except ImportError as import_error:
                    if ignore_errors:
                        logger.info('Module %s could not be imported: %s',
                                    module_name, import_error)
                    else:
                        raise
        return modules
