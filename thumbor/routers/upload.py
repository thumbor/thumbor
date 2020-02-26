#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import List, Optional, cast

from thumbor.handlers.image_resource import ImageResourceHandler
from thumbor.handlers.upload import ImageUploadHandler
from thumbor.routers.base import BaseRouter, Route


class UploadRouter(BaseRouter):
    def get_routes(self) -> Optional[List[Route]]:
        is_upload_enabled = cast(bool, self.context.config.UPLOAD_ENABLED)
        if not is_upload_enabled:
            return []

        return [
            Route(r"/image", ImageUploadHandler, {"context": self.context}),
            Route(r"/image/(.*)", ImageResourceHandler, {"context": self.context}),
        ]
