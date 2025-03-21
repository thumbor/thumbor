#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import glob
import logging
import os

from setuptools import Extension, setup

from pathlib import Path

try:
    import wheel.bdist_wheel
except ImportError:
    wheel = None

this_directory = Path(__file__).parent
long_description = (this_directory / "README.mkd").read_text(encoding="utf-8")

with open("thumbor/__init__.py") as f:
    ns = {}
    exec(f.read(), ns)
    version = ns["__version__"]

kwargs = {}

TESTS_REQUIREMENTS = [
    "coverage==7.*,>=7.4.0",
    "flake8==7.*,>=7.0.0",
    "isort==5.*,>=5.13.2",
    "pre-commit==3.*,>=3.6.0",
    "preggy==1.*,>=1.4.4",
    "pylint==3.*,>=3.0.3",
    "pyssim==0.*,>=0.7",
    "pytest==7.*,>=7.4.4",
    "pytest-asyncio==0.*,>=0.23.3",
    "pytest-cov==4.*,>=4.1.0",
    "pytest-tldr==0.*,>=0.2.5",
    "pytest-xdist==3.*,>=3.5.0",
    "redis==5.*,>=5.0.1",
    "remotecv==5.*,>=5.1.8",
    "sentry-sdk==1.*,>=1.39.1",
    "yanc==0.*,>=0.3.3",
]

OPENCV_REQUIREMENTS = [
    "opencv-python-headless==4.*,>=4.9.0.80",
    "numpy==1.*,>=1.26.3",
]

EXTRA_LIBS_REQUIREMENTS = [
    "cairosvg==2.*,>=2.7.1",
    "pycurl==7.*,>=7.45.2",
    "pillow-avif-plugin==1.*,>=1.4.1",
    "pillow-heif==0.*,>=0.14.0",
]

ALL_REQUIREMENTS = OPENCV_REQUIREMENTS + EXTRA_LIBS_REQUIREMENTS

if wheel is not None:
    # based on https://github.com/tornadoweb/tornado/blob/master/setup.py
    class bdist_wheel_abi3(wheel.bdist_wheel.bdist_wheel):
        def get_tag(self):
            python, abi, plat = super().get_tag()

            if python.startswith("cp"):
                return "cp39", "abi3", plat
            return python, abi, plat

    kwargs["cmdclass"] = {"bdist_wheel": bdist_wheel_abi3}


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


def run_setup(extension_modules=None):
    if extension_modules is None:
        extension_modules = []

    if "CFLAGS" not in os.environ:
        os.environ["CFLAGS"] = ""

    setup(
        name="thumbor",
        version=version,
        description="thumbor is an open-source photo thumbnail service by globo.com",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords="imaging face detection feature thumbnail imagemagick pil opencv",
        author="globo.com",
        author_email="thumbor@googlegroups.com",
        url="https://github.com/thumbor/thumbor/wiki",
        license="MIT",
        python_requires=">=3.9",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Multimedia :: Graphics :: Presentation",
        ],
        packages=["thumbor"],
        package_dir={"thumbor": "thumbor"},
        include_package_data=True,
        package_data={"": ["*.xml"]},
        install_requires=[
            "colorama==0.*,>=0.4.6",
            "derpconf==0.*,>=0.8.4",
            "JpegIPTC==1.*,>=1.5",
            "libthumbor==2.*,>=2.0.2",
            "piexif==1.*,>=1.1.3",
            "Pillow==10.*",
            "pytz==2023.*,>=2023.3.post1",
            "setuptools==75.*,>=75.2.0",
            "statsd==4.*,>=4.0.1",
            "thumbor-plugins-gifv==0.*,>=0.1.5",
            "tornado==6.*,>=6.4",
            "webcolors==1.*,>=1.13.0",
        ],
        extras_require={
            "all": ALL_REQUIREMENTS,
            "opencv": OPENCV_REQUIREMENTS,
            "tests": ALL_REQUIREMENTS + TESTS_REQUIREMENTS,
        },
        entry_points={
            "console_scripts": [
                "thumbor=thumbor.server:main",
                "thumbor-url=thumbor.url_composer:main",
                "thumbor-config=thumbor.config:generate_config",
                "thumbor-doctor=thumbor.doctor:main",
            ],
        },
        ext_modules=extension_modules,
        **kwargs,
    )


try:
    run_setup(gather_filter_extensions())
except SystemExit as exit_error:
    print(f"\n\n{'*' * 66}")
    logging.exception(exit_error)
    print(f"\n\n{'*' * 66}")
    print(
        "Couldn't build one or more native extensions"
        ", skipping compilation.\n\n"
    )
    run_setup()
