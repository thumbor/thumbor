#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from itertools import product

from colorama import Fore

DEBUGS = ["", "debug"]

METAS = ["meta"]

TRIMS = [
    "trim",
    "trim:top-left",
    "trim:bottom-right",
    "trim:top-left:10",
    "trim:bottom-right:20",
]

CROPS = ["10x10:100x100"]

FITINS = ["fit-in", "adaptive-fit-in", "full-fit-in", "adaptive-full-fit-in"]

SIZES = [
    "200x200",
    "-300x100",
    "100x-300",
    "-100x-300",
    "origx300",
    "200xorig",
    "origxorig",
]

H_ALIGNS = [
    "left",
    "right",
    "center",
]

V_ALIGNS = [
    "top",
    "bottom",
    "middle",
]

SMARTS = [
    "smart",
]

FILTERS = [
    "filters:brightness(10)",
    "filters:contrast(10)",
    "filters:equalize()",
    "filters:grayscale()",
    "filters:rotate(90)",
    "filters:noise(10)",
    "filters:quality(5)",
    "filters:redeye()",
    "filters:rgb(10,-10,20)",
    "filters:round_corner(20,255,255,100)",
    "filters:sharpen(6,2.5,false)",
    "filters:sharpen(6,2.5,true)",
    "filters:strip_exif()",
    "filters:strip_icc()",
    "filters:watermark(rgba-interlaced.png,10,10,50)",
    "filters:watermark(rgba-interlaced.png,center,center,50)",
    "filters:watermark(rgba-interlaced.png,repeat,repeat,50)",
    "filters:frame(rgba.png)",
    "filters:fill(ff0000)",
    "filters:fill(auto)",
    "filters:fill(ff0000,true)",
    "filters:fill(transparent)",
    "filters:fill(transparent,true)",
    "filters:blur(2)",
    "filters:extract_focal()",
    "filters:focal()",
    "filters:focal(0x0:1x1)",
    "filters:no_upscale()",
    "filters:gifv()",
    "filters:gifv(webm)",
    "filters:gifv(mp4)",
    "filters:max_age(600)",
    "filters:upscale()",
    "filters:format(avif)",
    "filters:format(heic)",
    "filters:format(heif)",
    # one big filter 4-line string
    "filters:curve([(0,0),(255,255)],[(0,50),(16,51),(32,69),"
    "(58,85),(92,120),(128,170),(140,186),(167,225),"  # NOQA
    "(192,245),(225,255),(244,255),(255,254)],[(0,0),(16,2),"
    "(32,18),(64,59),(92,116),(128,182),(167,211),(192,227)"  # NOQA
    ",(224,240),(244,247),(255,252)],[(0,48),(16,50),(62,77),"
    "(92,110),(128,144),(140,153),(167,180),(192,192),"  # NOQA
    "(224,217),(244,225),(255,225)])",
]

ORIGINAL_IMAGES_BASE = [
    "gradient.jpg",
    "cmyk.jpg",
    "rgba.png",
    "grayscale.jpg",
    "16bit.png",
    "thumbor-exif.png",
]

ORIGINAL_IMAGES_GIF_WEBP = [
    "gradient.webp",
    "gradient.gif",
    "animated.gif",
]

ALL_OPTIONS = (
    METAS
    + TRIMS
    + CROPS
    + FITINS
    + SIZES
    + H_ALIGNS
    + V_ALIGNS
    + SMARTS
    + FILTERS
)

MAX_DATASET_SIZE = len(ALL_OPTIONS) * (
    len(ORIGINAL_IMAGES_BASE) + len(ORIGINAL_IMAGES_GIF_WEBP)
)


class UrlsTester:
    def __init__(self, http_client):
        self.failed_items = []
        self.http_client = http_client

    def report(self):
        if len(self.failed_items) == 0:
            return

        raise AssertionError("Failed urls:\n%s" % "\n".join(self.failed_items))

    async def try_url(self, url):
        result = None
        error = None
        failed = False

        try:
            result = await self.http_client.fetch(url, request_timeout=60)
        except Exception as err:  # pylint: disable=broad-except
            logging.exception("Error in %s: %s", url, err)
            error = err
            failed = True

        if result is not None and result.code == 200 and not failed:
            print("{0.GREEN} SUCCESS ({1}){0.RESET}".format(Fore, url))
            return

        self.failed_items.append(url)
        print(
            "{0.RED} FAILED ({1}) - ERR({2}) {0.RESET}".format(
                Fore, url, result is not None and result.code or error
            )
        )


def single_dataset(with_gif=True):
    images = ORIGINAL_IMAGES_BASE[:]
    if with_gif:
        images += ORIGINAL_IMAGES_GIF_WEBP
    return product(ALL_OPTIONS, images)


def combined_dataset(with_gif=True):
    images = ORIGINAL_IMAGES_BASE[:]
    if with_gif:
        images += ORIGINAL_IMAGES_GIF_WEBP
    combined_options = product(
        TRIMS[:2],
        CROPS[:2],
        FITINS[:2],
        SIZES[:2],
        H_ALIGNS[:2],
        V_ALIGNS[:2],
        SMARTS[:2],
        FILTERS[:2],
        images,
    )
    return combined_options
