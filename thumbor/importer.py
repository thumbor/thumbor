#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

class Importer:
    def __init__(self, config):
        self.config = config
        self.config.validates_presence_of('ENGINE', 'LOADER', 'STORAGE', 'DETECTORS', 'FILTERS')

    def import_class(self, name):
        if not '.' in name:
            return __import__(name)

        module_name = '.'.join(name.split('.')[:-1])
        klass = name.split('.')[-1]

        module = __import__(module_name)
        if '.' in module_name:
            module = reduce(getattr, module_name.split('.')[1:], module)

        return getattr(module, klass)

    def import_modules(self):
        self.import_item('ENGINE', 'Engine')
        self.import_item('LOADER')
        self.import_item('STORAGE', 'Storage')
        self.import_item('DETECTORS', 'Detector')
        self.import_item('FILTERS', 'Filter')

    def import_item(self, config_key, class_name=None):
        conf_value = getattr(self.config, config_key)

        if isinstance(conf_value, (tuple, list)):
            modules = []
            for module_name in conf_value:
                if class_name is not None:
                    module = self.import_class('%s.%s' % (module_name, class_name))
                else:
                    module = self.import_class(module_name)
                modules.append(module)
            setattr(self, config_key.lower(), tuple(modules))
        else:
            if class_name is not None:
                module = self.import_class('%s.%s' % (conf_value, class_name))
            else:
                module = self.import_class(conf_value)
            setattr(self, config_key.lower(), module)

