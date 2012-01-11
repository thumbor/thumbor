#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor import filters

class Importer:
    def __init__(self, config):
        self.config = config
        self.config.validates_presence_of('ENGINE', 'LOADER', 'STORAGE', 'DETECTORS', 'FILTERS')

    def import_class(self, name, get_module=False):
        if not '.' in name:
            return __import__(name)

        module_name = get_module and name or '.'.join(name.split('.')[:-1])
        klass = name.split('.')[-1]

        module = get_module and __import__(name) or __import__(module_name)
        if '.' in module_name:
            module = reduce(getattr, module_name.split('.')[1:], module)

        return get_module and module or getattr(module, klass)

    def import_modules(self):
        self.import_item('ENGINE', 'Engine')
        self.import_item('LOADER')
        self.import_item('STORAGE', 'Storage')
        self.import_item('DETECTORS', 'Detector', is_multiple=True)
        self.import_item('FILTERS', 'Filter', is_multiple=True)

        filters.compile_filters(self.filters)

    def import_item(self, config_key, class_name=None, is_multiple=False):
        conf_value = getattr(self.config, config_key)

        if is_multiple:
            modules = []
            if conf_value:
                for module_name in conf_value:
                    if class_name is not None:
                        module = self.import_class('%s.%s' % (module_name, class_name))
                    else:
                        module = self.import_class(module_name, get_module=True)
                    modules.append(module)
            setattr(self, config_key.lower(), tuple(modules))
        else:
            if class_name is not None:
                module = self.import_class('%s.%s' % (conf_value, class_name))
            else:
                module = self.import_class(conf_value, get_module=True)
            setattr(self, config_key.lower(), module)

