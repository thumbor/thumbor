#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from tornado.web import RequestHandler


class Route:
    def __init__(
        self, url: str, handler: RequestHandler, initialize: Dict[str, Any] = None
    ):
        self.url = url
        self.handler = handler
        self.initialize = initialize


class BaseRouter(ABC):
    def __init__(self, context: Any):
        self.context = context

    @abstractmethod
    def get_routes(self) -> Optional[List[Route]]:
        pass
