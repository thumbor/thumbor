# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import thumbor.handler_lists.upload as handler_list
from thumbor.handlers.image_resource import ImageResourceHandler
from thumbor.handlers.upload import ImageUploadHandler
from thumbor.testing import TestCase


class UploadHandlerListTestCase(TestCase):
    def test_can_get_handlers(self):
        ctx = self.get_context()
        ctx.config.UPLOAD_ENABLED = True

        handlers = handler_list.get_handlers(ctx)

        assert handlers is not None
        assert len(handlers) == 2
        url, handler, init = handlers[0]
        assert url == r"/image"
        assert handler == ImageUploadHandler
        assert init == {"context": ctx}
        url, handler, init = handlers[1]
        assert url == r"/image/(.*)"
        assert handler == ImageResourceHandler
        assert init == {"context": ctx}

    def test_can_disable_upload(self):
        ctx = self.get_context()
        ctx.config.UPLOAD_ENABLED = False

        handlers = handler_list.get_handlers(ctx)

        assert handlers is not None
        assert not handlers
