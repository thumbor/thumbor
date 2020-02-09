#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import List, Optional, cast

from thumbor.handlers.healthcheck import HealthcheckHandler
from thumbor.routers.base import BaseRouter, Route


class HealthcheckRouter(BaseRouter):
    def get_routes(self) -> Optional[List[Route]]:
        url = cast(str, self.context.config.HEALTHCHECK_ROUTE)
        return [Route(url, HealthcheckHandler)]
