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

from thumbor import __version__

tests_require = [
    "redis>=2.4.9,<3.0.0",
    "coverage>=4.4.1",
    "mock>=1.0.1,<3.0.0",
    "sentry-sdk",
    "nose",
    "nose-focus",
    "colorama",
    "numpy",
    "flake8",
    "yanc",
    "remotecv",
    "pyssim>=0.4.0",
    "cairosvg>=1.0.0,<2.0.0,!=1.0.21",
    "preggy>=1.3.0",
    "opencv-python-headless",
    "yanc>=0.3.3",
    "py3exiv2",
]


def filter_extension_module(name, lib_objs, lib_headers):
    return Extension(
        "thumbor.ext.filters.%s" % name,
        ["thumbor/ext/filters/%s.c" % name] + lib_objs,
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


def run_setup(extension_modules=[]):
    if "CFLAGS" not in os.environ:
        os.environ["CFLAGS"] = ""
    setup(
        name="thumbor",
        version=__version__,
        description=(
            "thumbor is an open-source photo thumbnail service by globo.com"
        ),
        long_description="""
Thumbor is a smart imaging service. It enables on-demand crop,
resizing and flipping of images.

<<<<<<< HEAD
It also features a VERY smart detection of important points in
the image for better cropping and resizing, using state-of-the-art
face and feature detection algorithms (more on that in Detection Algorithms).

Using thumbor is very easy (after it is running). All you have to do is
access it using an url for an image, like this:
=======
It also features a VERY smart detection of important points in the
image for better cropping and resizing, using state-of-the-art face
and feature detection algorithms (more on that in Detection Algorithms).

Using thumbor is very easy (after it is running). All you have to do
is access it using an url for an image, like this:
>>>>>>> Updating test running and Linux support in tests

http://<thumbor-server>/300x200/smart/thumbor.readthedocs.io/en/latest/_images/logo-thumbor.png
""",
        keywords=(
            "imaging face detection feature thumbnail imagemagick pil opencv"
        ),
        author="globo.com",
        author_email="thumbor@googlegroups.com",
        url="https://github.com/thumbor/thumbor/wiki",
        license="MIT",
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
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Multimedia :: Graphics :: Presentation",
        ],
        packages=["thumbor"],
        package_dir={"thumbor": "thumbor"},
        include_package_data=True,
        package_data={"": ["*.xml"]},
        install_requires=[
            "tornado>=4.1.0,<6.0.0",
            "pycurl>=7.19.0,<7.44.0",
            "Pillow>=4.3.0,<7",
            "derpconf>=0.2.0",
            "statsd>=3.0.1",
            "libthumbor>=1.3.2",
            "pytz",
            "webcolors",
        ],
        extras_require={"tests": tests_require},
        entry_points={
            "console_scripts": [
                "thumbor=thumbor.server:main",
                "thumbor-url=thumbor.url_composer:main",
                "thumbor-config=thumbor.config:generate_config",
            ],
        },
        ext_modules=extension_modules,
    )


try:
    run_setup(gather_filter_extensions())
except SystemExit as exit:
    print("\n\n%s" % ("*" * 66))
    logging.exception(exit)
    print("\n\n%s" % ("*" * 66))
    print(
        "Couldn't build one or more native extensions, "
        "skipping compilation.\n\n"
    )
    run_setup()
