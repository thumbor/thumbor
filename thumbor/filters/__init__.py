#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import collections
import re

BUILTIN_FILTERS = [
    "thumbor.filters.brightness",
    "thumbor.filters.colorize",
    "thumbor.filters.contrast",
    "thumbor.filters.rgb",
    "thumbor.filters.round_corner",
    "thumbor.filters.quality",
    "thumbor.filters.noise",
    "thumbor.filters.watermark",
    "thumbor.filters.equalize",
    "thumbor.filters.fill",
    "thumbor.filters.sharpen",
    "thumbor.filters.strip_exif",
    "thumbor.filters.strip_icc",
    "thumbor.filters.frame",
    "thumbor.filters.grayscale",
    "thumbor.filters.rotate",
    "thumbor.filters.format",
    "thumbor.filters.max_bytes",
    "thumbor.filters.convolution",
    "thumbor.filters.blur",
    "thumbor.filters.extract_focal",
    "thumbor.filters.focal",
    "thumbor.filters.no_upscale",
    "thumbor.filters.saturation",
    "thumbor.filters.max_age",
    "thumbor.filters.curve",
    "thumbor.filters.background_color",
    "thumbor.filters.upscale",
    "thumbor.filters.proportion",
    "thumbor.filters.stretch",
]

STRIP_QUOTE = re.compile(r"^'(.+)'$")
PHASE_POST_TRANSFORM = "post_transform"
PHASE_PRE_LOAD = "pre-load"
PHASE_AFTER_LOAD = "after-load"


def filter_method(*args):
    def _filter_deco(filtered_function):
        async def wrapper(self, *args2):
            return await filtered_function(self, *args2)

        defaults = None
        if filtered_function.__defaults__:
            default_padding = [None] * (
                len(args) - (len(filtered_function.__defaults__))
            )
            defaults = default_padding + list(filtered_function.__defaults__)

        wrapper.filter_data = {
            "name": filtered_function.__name__,
            "params": args,
            "defaults": defaults,
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

        filter_params = filter_params.split("):")
        last_idx = len(filter_params) - 1

        for i, param in enumerate(filter_params):
            filter_name = param.split("(")[0]
            cls = self.filter_classes_map.get(filter_name, None)

            if cls is None:
                continue

            if i != last_idx:
                param = param + ")"
            instance = cls.init_if_valid(param, context)

            if instance:
                filter_instances[
                    getattr(cls, "phase", PHASE_POST_TRANSFORM)
                ].append(instance)

        return FiltersRunner(filter_instances)


class FiltersRunner:
    def __init__(self, filter_instances):
        self.filter_instances = filter_instances

    async def apply_filters(self, phase):
        filters = self.filter_instances.get(phase, None)
        if not filters:
            return None

        while filters:
            filter_to_run = filters.pop(0)
            await filter_to_run.run()


class BaseFilter:
    PositiveNumber = {"regex": r"[\d]+", "parse": int}
    PositiveNonZeroNumber = {"regex": r"[\d]*[1-9][\d]*", "parse": int}
    NegativeNumber = {
        "regex": f"[-]{PositiveNumber['regex']}",
        "parse": int,
    }
    Number = {"regex": f"[-]?{PositiveNumber['regex']}", "parse": int}
    DecimalNumber = {
        "regex": r"[-]?(?:(?:[\d]+\.?[\d]*)|(?:[\d]*\.?[\d]+))",
        "parse": float,
    }
    Boolean = {
        "regex": r"[Tt]rue|[Ff]alse|1|0",
        "parse": lambda v: v in ("true", "True", "1"),
    }
    String = {
        "regex": r"(?:'.+?')|(?:[^,]+?)",
        "parse": lambda v: STRIP_QUOTE.sub(r"\1", v),
    }

    @classmethod
    def pre_compile(cls):
        meths = [
            f for f in list(cls.__dict__.values()) if hasattr(f, "filter_data")
        ]
        if len(meths) == 0:
            return None
        cls.runnable_method = meths[0]
        filter_data = cls.runnable_method.filter_data

        cls.compile_regex(filter_data)
        return filter_data["name"]

    @classmethod
    def compile_regex(cls, filter_data):
        params = filter_data["params"]
        defaults = filter_data.get("defaults", None)
        regexes = []
        parsers = []
        for i, param in enumerate(params):
            val = (
                (param["regex"], param["parse"])
                if (isinstance(param, dict))
                else (param, None)
            )
            comma = optional = ""
            if defaults and defaults[i] is not None:
                optional = "?"
            if i > 0:
                comma = ","
            regexes.append(f"(?:{comma}\\s*({val[0]})\\s*){optional}")
            parsers.append(val[1])

        cls.parsers = parsers
        cls.regex_str = f"{filter_data['name']}\\({''.join(regexes)}\\)"
        cls.regex = re.compile(cls.regex_str)

    @classmethod
    def init_if_valid(cls, param, context):
        instance = cls(param, context)
        if instance.params is not None:
            return instance
        return None

    def __init__(self, params, context=None):
        params = self.regex.match(params) if self.regex else None
        if params:
            params = [
                parser(param) if parser else param
                for parser, param in zip(self.parsers, params.groups())
                if param
            ]
        self.params = params
        self.context = context
        self.engine = (
            context.modules.engine if context and context.modules else None
        )

    async def run(self):
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
        for engine in engines_to_run:
            self.engine = engine
            results.append(await self.runnable_method(*self.params))

        return results
