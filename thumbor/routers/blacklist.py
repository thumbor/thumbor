#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import List, Optional, cast

from thumbor.handlers.blacklist import BlacklistHandler
from thumbor.routers.base import BaseRouter, Route


class BlacklistRouter(BaseRouter):
    def get_routes(self) -> Optional[List[Route]]:
        is_blacklist_enabled = cast(bool, self.context.config.USE_BLACKLIST)
        if not is_blacklist_enabled:
            return []

        return [Route(r"/blacklist/?", BlacklistHandler, {"context": self.context})]
