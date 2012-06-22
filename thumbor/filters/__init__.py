#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re

def filter_method(*args, **kwargs):
    def _filter_deco(fn):
        def wrapper(self, *args2):
            return fn(self, *args2)
        wrapper.filter_data = {
            'name': fn.__name__,
            'params': args,
            'async': kwargs.get('async', False)
        }
        return wrapper
    return _filter_deco


class FiltersFactory:

    def __init__(self, filter_classes):
        self.filter_classes_map = {}

        for cls in filter_classes:
            filter_name = cls.pre_compile()
            self.filter_classes_map[filter_name] = cls

    def create_instances(self, context, filter_params):
        filter_params = filter_params.split('):')
        filter_objs = []

        for param in filter_params:
            filter_name = param.split('(')[0]
            cls = self.filter_classes_map[filter_name]
            instance = cls.init_if_valid(param + ')', context)

            if instance:
                filter_objs.append(instance)
        return filter_objs


class BaseFilter(object):

    PositiveNumber = {
        'regex': r'[\d]+',
        'parse': int
    }
    NegativeNumber = {
        'regex': r'[-]%s' % PositiveNumber['regex'],
        'parse': int
    }
    Number = {
        'regex': r'[-]?%s' % PositiveNumber['regex'],
        'parse': int
    }
    DecimalNumber = {
        'regex': r'[-]?(?:(?:[\d]+\.?[\d]*)|(?:[\d]*\.?[\d]+))',
        'parse': float
    }
    Boolean = {
        'regex': r'[Tt]rue|[Ff]alse|1|0',
        'parse': lambda v: v == 'true' or v == 'True' or v == '1'
    }
    String = r'[^,]+?'

    @classmethod
    def pre_compile(cls):
        meths = filter(lambda f: hasattr(f, 'filter_data'), cls.__dict__.values())
        if len(meths) == 0:
            return
        cls.runnable_method = meths[0]
        filter_data = cls.runnable_method.filter_data

        cls.async_filter = filter_data['async']
        cls.compile_regex(filter_data)
        return filter_data['name']

    @classmethod
    def compile_regex(cls, filter_data):
        params = filter_data['params']
        regexes = []
        parsers = []
        for f in params:
            val = (type(f) == dict) and (f['regex'], f['parse']) or (f, None)
            regexes.append(val[0])
            parsers.append(val[1])

        cls.parsers = parsers
        cls.regex_str = r'%s\(\s*(%s)\s*\)' % (filter_data['name'], ')\\s*,\\s*('.join(regexes))
        cls.regex = re.compile(cls.regex_str)

    @classmethod
    def init_if_valid(cls, param, context):
        instance = cls(param, context)
        if instance.params is not None:
            return instance
        else:
            return None

    def __init__(self, params, context = None):
        params = self.regex.match(params) if self.regex else None
        if params:
            params = [parser(param) if parser else param for parser, param in zip(self.parsers, params.groups())]
        self.params = params
        self.context = context
        self.engine = context.modules.engine if context and context.modules else None

    def run(self, callback = None):
        if self.params is not None:
            if self.async_filter:
                self.runnable_method(callback, *self.params)
            else:
                ret = self.runnable_method(*self.params)
                if callback:
                    callback()
                return ret 
