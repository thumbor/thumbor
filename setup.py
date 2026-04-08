# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import glob
import os
import sys

from setuptools import setup

try:
    from setuptools_rust import RustExtension
except ImportError:
    RustExtension = None

try:
    import wheel.bdist_wheel
except ImportError:
    wheel = None

kwargs = {}

if wheel is not None:
    # based on https://github.com/tornadoweb/tornado/blob/master/setup.py
    class bdist_wheel_abi3(wheel.bdist_wheel.bdist_wheel):
        def get_tag(self):
            python, abi, plat = super().get_tag()

            if python.startswith("cp"):
                return "cp39", "abi3", plat
            return python, abi, plat

    kwargs["cmdclass"] = {"bdist_wheel": bdist_wheel_abi3}


def gather_rust_filter_extensions():
    if RustExtension is None:
        return []

    cargo_paths = glob.glob("thumbor/ext/filters/_*/Cargo.toml")

    return [
        RustExtension(
            f"thumbor.ext.filters.{os.path.basename(os.path.dirname(path))}",
            path=path,
        )
        for path in cargo_paths
    ]


def ensure_build_dependencies():
    build_commands = {
        "bdist_wheel",
        "build",
        "build_ext",
        "develop",
        "editable_wheel",
        "install",
    }

    if RustExtension is None and any(
        arg in build_commands for arg in sys.argv[1:]
    ):
        raise RuntimeError(
            "setuptools-rust is required to build thumbor's Rust filters. "
            "Install dependencies with `pip install -e .[tests,all]`."
        )


ensure_build_dependencies()
setup_kwargs = dict(kwargs)

if RustExtension is not None:
    setup_kwargs["rust_extensions"] = gather_rust_filter_extensions()

setup(**setup_kwargs)
