# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import glob

from setuptools import Extension, setup


def filter_extension_module(name, lib_objs, lib_headers):
    return Extension(
        f"thumbor.ext.filters.{name}",
        [f"thumbor/ext/filters/{name}.c"] + lib_objs,
        libraries=["m"],
        include_dirs=["thumbor/ext/filters/lib"],
        depends=["setup.py"] + lib_objs + lib_headers,
        extra_compile_args=[
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-unused-parameter",
        ],
        py_limited_api=True,
        define_macros=[("Py_LIMITED_API", "0x03080000")],
    )


def gather_filter_extensions():
    files = glob.glob("thumbor/ext/filters/_*.c")
    lib_objs = glob.glob("thumbor/ext/filters/lib/*.c")
    lib_headers = glob.glob("thumbor/ext/filters/lib/*.h")

    return [
        filter_extension_module(f[0:-2].split("/")[-1], lib_objs, lib_headers)
        for f in files
    ]


setup(ext_modules=gather_filter_extensions())
