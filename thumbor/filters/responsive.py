# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com# coding: utf-8

from __future__ import unicode_literals, absolute_import
from thumbor.filters import BaseFilter, filter_method, PHASE_PRE_LOAD
from thumbor.utils import logger

class Filter(BaseFilter):
    """
    This filter adds display resolution information to the context. It
    allows to create retina images.
    If this filter is active and a user requests a 320x240 image with a dpr of 2,
    then a 640x480 image could be delivered. The output size depends on other
    things as well such as the source image resolution and the network quality.

    usage: /filters:dpr(2)/ or /filters:dpr()/

    If no argument is given, then a dpr of 1 is assumed. Except if Client hints
    are available. Then that dpr value is considered.
    """
    phase = PHASE_PRE_LOAD

    MIN_DPR = 0.5
    MAX_DPR = 4.0
    MIN_DOWNLINK = 1.0  # mbit/s

    @filter_method(r'(0\.[5-9]([0-9]*)?|[1-4](\.[0-9]+)?)?')  #
    def responsive(self, initial_dpr=None):
        logger.debug('DPR filter activated. Initial value: %s ' % initial_dpr)

        dpr = self._get_dpr(initial_dpr, self.context.request.headers)

        if self.context and self.context.request:
            self.context.request.dpr = dpr

    def _get_dpr(self, initial_dpr, request_headers):
        """
        Returns the display resolution factor. The passed in values override
        the client hint values. A slow connection reduces the dpr to a minimum.
        :param initial_dpr: values from the URL
        :type initial_dpr: float
        :param request_headers: HTTP Request Headers
        :type request_headers: dict
        :return: Calculated values
        :rtype: float
        """
        dpr = 1.0

        # Check if the dpr was sent with HTTP Client Hints
        header_dpr = request_headers.get('Dpr')
        if header_dpr is not None:
            logger.debug('Dpr in header found. Using this value: %s'
                         % header_dpr)
            dpr = float(header_dpr)
            self.context.vary_headers.add('Dpr')

        # args can override Headers
        if initial_dpr:
            initial_dpr = float(initial_dpr)
            if self.MIN_DPR <= initial_dpr <= self.MAX_DPR:
                dpr = initial_dpr
            else:
                logger.debug('Illegal dpr value: %s' % initial_dpr)

        # Check if the downlink speed is fast enough for retina images
        header_downlink = request_headers.get('Downlink')
        if header_downlink and float(header_downlink) < self.MIN_DOWNLINK:
            dpr = min(dpr, 1.0)
            self.context.vary_headers.add('Downlink')

        return dpr
