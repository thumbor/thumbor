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

try:
    from thumbor import __version__
except ImportError:
    __version__ = "0.0.0"

TESTS_REQUIREMENTS = [
    "coverage==6.*,>=6.3.2",
    "flake8==3.*,>=3.7.9",
    "isort==4.*,>=4.3.21",
    "pre-commit==2.*,>=2.17.0",
    "preggy==1.*,>=1.4.4",
    "pylint==2.*,>=2.4.4",
    "pyssim==0.*,>=0.4.0",
    "pytest>=6.2.5",
    "pytest-asyncio==0.*,>=0.10.0",
    "pytest-cov==3.*,>=3.0.0",
    "pytest-tldr==0.*,>=0.2.1",
    "pytest-xdist==2.*,>=2.4.0",
    "redis==3.*,>=3.4.0",
    "remotecv>=2.3.0",
    "sentry-sdk==0.*,>=0.14.1",
    "yanc==0.*,>=0.3.3",
]

OPENCV_REQUIREMENTS = [
    "opencv-python-headless==4.*,>=4.2.0",
    "numpy==1.*,>=1.18.1",
]

EXTRA_LIBS_REQUIREMENTS = [
    # Going to update in a proper commit
    "cairosvg>=2.5.2",
    "pycurl==7.*,>=7.43.0",
    "py3exiv2>=0.*,<0.7.2",
]

ALL_REQUIREMENTS = OPENCV_REQUIREMENTS + EXTRA_LIBS_REQUIREMENTS


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
        version=__version__,
        description="thumbor is an open-source photo thumbnail service by globo.com",
        long_description="""
Thumbor is a smart imaging service. It enables on-demand crop, resizing and flipping of images.

It also features a VERY smart detection of important points in the image for better cropping and
resizing, using state-of-the-art face and feature detection algorithms (more on that in Detection Algorithms).

Using thumbor is very easy (after it is running). All you have to do is access it using an url for an image, like this:

http://<thumbor-server>/300x200/smart/thumbor.readthedocs.io/en/latest/_images/logo-thumbor.png
""",
        keywords="imaging face detection feature thumbnail imagemagick pil opencv",
        author="globo.com",
        author_email="thumbor@googlegroups.com",
        url="https://github.com/thumbor/thumbor/wiki",
        license="MIT",
        python_requires=">=3.6",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Multimedia :: Graphics :: Presentation",
        ],
        packages=["thumbor"],
        package_dir={"thumbor": "thumbor"},
        include_package_data=True,
        package_data={"": ["*.xml"]},
        install_requires=[
            "colorama==0.*,>=0.4.3",
            "derpconf==0.*,>=0.8.3",
            "libthumbor==2.*,>=2.0.2",
            "Pillow>=9.0.0",
            "pytz>=2019.3.0",
            "statsd==3.*,>=3.3.0",
            "tornado==6.*,>=6.0.3",
            "thumbor-plugins-gifv==0.*,>=0.1.2",
            "webcolors==1.*,>=1.10.0",
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
