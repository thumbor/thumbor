#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from itertools import product

from colorama import Fore

debugs = ["", "debug"]

metas = ["meta"]

trims = [
    "trim",
    "trim:top-left",
    "trim:bottom-right",
    "trim:top-left:10",
    "trim:bottom-right:20",
]

crops = ["10x10:100x100"]

fitins = ["fit-in", "adaptive-fit-in", "full-fit-in", "adaptive-full-fit-in"]

sizes = [
    "200x200",
    "-300x100",
    "100x-300",
    "-100x-300",
    "origx300",
    "200xorig",
    "origxorig",
]

haligns = [
    "left",
    "right",
    "center",
]

valigns = [
    "top",
    "bottom",
    "middle",
]

smarts = [
    "smart",
]

filters = [
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
    # one big filter 4-line string
    "filters:curve([(0,0),(255,255)],[(0,50),(16,51),(32,69),(58,85),(92,120),(128,170),(140,186),(167,225),"  # NOQA
    "(192,245),(225,255),(244,255),(255,254)],[(0,0),(16,2),(32,18),(64,59),(92,116),(128,182),(167,211),(192,227)"  # NOQA
    ",(224,240),(244,247),(255,252)],[(0,48),(16,50),(62,77),(92,110),(128,144),(140,153),(167,180),(192,192),"  # NOQA
    "(224,217),(244,225),(255,225)])",
]

original_images_base = [
    "gradient.jpg",
    "cmyk.jpg",
    "rgba.png",
    "grayscale.jpg",
    "16bit.png",
]

original_images_gif_webp = [
    "gradient.webp",
    "gradient.gif",
    "animated.gif",
]


class UrlsTester(object):
    def __init__(self, http_client):
        self.failed_items = []
        self.http_client = http_client

    def report(self):
        assert len(self.failed_items) == 0, "Failed urls:\n%s" % "\n".join(
            self.failed_items
        )

    async def try_url(self, url):
        result = None
        error = None
        failed = False

        try:
            result = await self.http_client.fetch(url, request_timeout=30)
        except Exception as err:
            logging.exception("Error in %s: %s" % (url, err))
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
    images = original_images_base[:]
    if with_gif:
        images += original_images_gif_webp
    all_options = (
        metas
        + trims
        + crops
        + fitins
        + sizes
        + haligns
        + valigns
        + smarts
        + filters
    )
    return product(all_options, images)


def combined_dataset(fetcher, with_gif=True):
    images = original_images_base[:]
    if with_gif:
        images += original_images_gif_webp
    combined_options = product(
        trims[:2],
        crops[:2],
        fitins[:2],
        sizes[:2],
        haligns[:2],
        valigns[:2],
        smarts[:2],
        filters[:2],
        images,
    )
    return combined_options
