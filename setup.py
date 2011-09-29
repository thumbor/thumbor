#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from setuptools import setup, Extension
from thumbor import __version__

setup(
    name = 'thumbor',
    version = __version__,
    description = "thumbor is an open-source photo thumbnail service by globo.com",
    long_description = """
Thumbor is a smart imaging service. It enables on-demand crop, resizing and flipping of images.

It also features a VERY smart detection of important points in the image for better cropping and resizing, using state-of-the-art face and feature detection algorithms (more on that in Detection Algorithms).

Using thumbor is very easy (after it is running). All you have to do is access it using an url for an image, like this:

http://<thumbor-server>/300x200/smart/s.glbimg.com/et/bb/f/original/2011/03/24/VN0JiwzmOw0b0lg.jpg
""",    
    keywords = 'imaging face detection feature thumbnail imagemagick pil opencv',
    author = 'globo.com',
    author_email = 'timehome@corp.globo.com',
    url = 'https://github.com/globocom/thumbor/wiki',
    license = 'MIT',
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    packages = ['thumbor'],
    package_dir = {"thumbor": "thumbor"},
    include_package_data = True,
    package_data = {
        '': ['*.xml'],
    },

    install_requires=[
        "tornado==1.2.1",
        "redis",
        "pyCrypto",
        "pycurl",
        "pillow"
    ],

    entry_points = {
        'console_scripts': [
            'thumbor = thumbor.server:main',
            'thumbor-url = thumbor.url_composer:main'
        ],
    },

    ext_modules = [
      Extension('thumbor.ext.filters._brightness', ['thumbor/ext/filters/_brightness.c']),
      Extension('thumbor.ext.filters._contrast', ['thumbor/ext/filters/_contrast.c']),
      Extension('thumbor.ext.filters._rgb', ['thumbor/ext/filters/_rgb.c']),
      Extension('thumbor.ext.filters._round_corner', ['thumbor/ext/filters/_round_corner.c'])
    ]
)


