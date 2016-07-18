#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import re
import collections

STRIP_QUOTE = re.compile(r"^'(.+)'$")
PHASE_POST_TRANSFORM = 'post_transform'
PHASE_PRE_LOAD = 'pre-load'
PHASE_AFTER_LOAD = 'after-load'


def filter_method(*args, **kwargs):
    def _filter_deco(fn):
        def wrapper(self, *args2):
            return fn(self, *args2)

        defaults = None
        if fn.__defaults__:
            default_padding = [None] * (len(args) - (len(fn.__defaults__)))
            defaults = default_padding + list(fn.__defaults__)

        wrapper.filter_data = {
            'name': fn.__name__,
            'params': args,
            'defaults': defaults,
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
        filter_instances = collections.defaultdict(list)
        if not filter_params:
            return FiltersRunner(filter_instances)

        filter_params = filter_params.split('):')
        last_idx = len(filter_params) - 1

        for i, param in enumerate(filter_params):
            filter_name = param.split('(')[0]
            cls = self.filter_classes_map.get(filter_name, None)

            if cls is None:
                continue

            if i != last_idx:
                param = param + ')'
            instance = cls.init_if_valid(param, context)

            if instance:
                filter_instances[getattr(cls, 'phase', PHASE_POST_TRANSFORM)].append(instance)

        return FiltersRunner(filter_instances)


class FiltersRunner:
    def __init__(self, filter_instances):
        self.filter_instances = filter_instances

    def apply_filters(self, phase, callback):
        filters = self.filter_instances.get(phase, None)
        if not filters:
            callback()
            return

        def exec_one_filter():
            if len(filters) == 0:
                callback()
                return

            f = filters.pop(0)
            f.run(exec_one_filter)
        exec_one_filter()


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
    String = {
        'regex': r"(?:'.+?')|(?:[^,]+?)",
        'parse': lambda v: STRIP_QUOTE.sub(r'\1', v)
    }

    @classmethod
    def pre_compile(cls):
        meths = [f for f in list(cls.__dict__.values()) if hasattr(f, 'filter_data')]
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
        defaults = filter_data.get('defaults', None)
        regexes = []
        parsers = []
        for i, param in enumerate(params):
            val = (type(param) == dict) and (param['regex'], param['parse']) or (param, None)
            comma = optional = ''
            if defaults and defaults[i] is not None:
                optional = '?'
            if i > 0:
                comma = ','
            regexes.append(r'(?:%s\s*(%s)\s*)%s' % (comma, val[0], optional))
            parsers.append(val[1])

        cls.parsers = parsers
        cls.regex_str = r'%s\(%s\)' % (filter_data['name'], ''.join(regexes))
        cls.regex = re.compile(cls.regex_str)

    @classmethod
    def init_if_valid(cls, param, context):
        instance = cls(param, context)
        if instance.params is not None:
            return instance
        else:
            return None

    def __init__(self, params, context=None):
        params = self.regex.match(params) if self.regex else None
        if params:
            params = [parser(param) if parser else param for parser, param in zip(self.parsers, params.groups()) if param]
        self.params = params
        self.context = context
        self.engine = context.modules.engine if context and context.modules else None

    def create_multi_engine_callback(self, callback, engines_count):
        self.engines_count = engines_count

        def single_callback(*args):
            self.engines_count -= 1
            if self.engines_count == 0:
                callback(*args)
        return single_callback

    def run(self, callback=None):
        if self.params is None:
            return

        if self.engine:
            if self.engine.is_multiple():
                engines_to_run = self.engine.frame_engines()
            else:
                engines_to_run = [self.engine]
        else:
            engines_to_run = [None]

        results = []
        if self.async_filter:
            callback = self.create_multi_engine_callback(callback, len(engines_to_run))
        for engine in engines_to_run:
            self.engine = engine
            if self.async_filter:
                self.runnable_method(callback, *self.params)
            else:
                results.append(self.runnable_method(*self.params))

        if (not self.async_filter) and callback:
            callback()

        return results
