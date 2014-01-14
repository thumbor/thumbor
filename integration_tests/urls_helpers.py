#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from os.path import join
from itertools import product

from colorama import Fore


debugs = [
    '',
    'debug'
]

metas = [
    '',
    'meta'
]

trims = [
    '',
    'trim',
    'trim:top-left',
    'trim:bottom-right',
    'trim:top-left:10',
    'trim:bottom-right:20',
]

crops = [
    '',
    '10x10:100x100'
]

fitins = [
    '',
    'fit-in',
    'adaptive-fit-in',
    'full-fit-in',
    'adaptive-full-fit-in'
]

sizes = [
    '',
    '200x200',
    '-300x100',
    '100x-300',
    '-100x-300',
    'origx300',
    '200xorig',
    'origxorig',
]

haligns = [
    '',
    'left',
    'right',
    'center',
]

valigns = [
    '',
    'top',
    'bottom',
    'middle',
]

smarts = [
    '',
    'smart',
]

filters = [
    '',
    'filters:brightness(10)',
    'filters:contrast(10)',
    'filters:equalize()',
    'filters:grayscale()',
    'filters:noise(10)',
    'filters:quality(5)',
    'filters:redeye()',
    'filters:rgb(10,-10,20)',
    'filters:round_corner(20,255,255,100)',
    'filters:sharpen(6,2.5,false)',
    'filters:strip_icc()',
    'filters:watermark(http://s.glbimg.com/es/ge/f/original/2012/08/15/brasil_45.png,10,10,50)',
    'filters:frame(publicobject.com/ninepatch/frame.9.png)',
    'filters:fill(ff0000)'
]

original_images_base = [
    's.glbimg.com/en/ho/f/original/2012/10/29/dilmahaddad.jpg',
    'g1.globo.com/platb/files/2135/2012/05/logo-FV.png-menor.png',
]

original_images_gif_webp = [
    'www.gstatic.com/webp/gallery/5.webp',
    'globoesporte.globo.com/platb/files/1031/2011/02/alerta.gif',
    'edgblogs.s3.amazonaws.com/bombounaweb/files/2012/09/tumblr_m9u52mZMgk1qz99y7o1_400.gif',
]


class UrlsTester(object):

    def __init__(self, fetcher, group):
        self.failed_items = []
        self.test_group(fetcher, group)

    def report(self):
        assert len(self.failed_items) == 0, "Failed urls:\n%s" % '\n'.join(self.failed_items)

    def try_url(self, fetcher, url):
        result = None
        failed = False

        try:
            result = fetcher("/%s" % url)
        except Exception:
            logging.exception('Error in %s' % url)
            failed = True

        if result is not None and result.code == 200 and not failed:
            print("{0.GREEN} SUCCESS ({1}){0.RESET}".format(Fore, url))
            return

        self.failed_items.append(url)
        print("{0.RED} FAILED ({1}) - ERR({2}) {0.RESET}".format(Fore, url, result and result.code))

    def test_group(self, fetcher, group):
        group = list(group)
        count = len(group)

        print("Requests count: %d" % count)
        for options in group:
            joined_parts = join(*options)
            url = "unsafe/%s" % joined_parts
            self.try_url(fetcher, url)

        self.report()


def single_dataset(fetcher, with_gif=True):
    images = original_images_base[:]
    if with_gif:
        images += original_images_gif_webp
    all_options = trims + crops + fitins + sizes + haligns + valigns + smarts + filters
    UrlsTester(fetcher, product(all_options, images))


def combined_dataset(fetcher, with_gif=True):
    images = original_images_base[:]
    if with_gif:
        images += original_images_gif_webp
    combined_options = product(trims[:2], crops[:2], fitins[:2], sizes[:2], haligns[:2], valigns[:2], smarts[:2], filters[:2], images)
    UrlsTester(fetcher, combined_options)
