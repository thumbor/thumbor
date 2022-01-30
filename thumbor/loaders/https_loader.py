#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.loaders import http_loader


def _normalize_url(url):
    url = http_loader.quote_url(url)
    return url if url.startswith("http") else f"https://{url}"


def validate(context, url):
    return http_loader.validate(
        context, url, normalize_url_func=_normalize_url
    )


async def load(context, url):
    return await http_loader.load(
        context,
        url,
        normalize_url_func=_normalize_url,
    )
