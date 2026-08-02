# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 globo.com thumbor@googlegroups.com

from types import SimpleNamespace
from unittest import mock

from preggy import expect

from thumbor.config import Config
from thumbor.context import RequestParameters
from thumbor.handlers import BaseHandler


def make_context(auto_webp=True, accepts_webp=True, headers=None):
    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.can_convert_to_webp.return_value = True
    request = SimpleNamespace(
        accepts_webp=accepts_webp,
        engine=engine,
        headers=headers,
    )

    return SimpleNamespace(
        config=SimpleNamespace(AUTO_WEBP=auto_webp),
        request=request,
    )


def make_handler(context, handler_class=BaseHandler):
    handler = object.__new__(handler_class)
    handler.context = context
    return handler


def test_accepts_mime_type_keeps_legacy_header_lookup():
    context = make_context(
        headers={"Accept": "image/avif,image/webp,*/*;q=0.8"}
    )
    handler = make_handler(context)

    expect(handler.accepts_mime_type("image/webp")).to_be_true()
    expect(handler.accepts_mime_type("image/png")).to_be_false()


def test_accepts_mime_type_without_headers_returns_false():
    context = make_context(headers=None)
    handler = make_handler(context)

    expect(handler.accepts_mime_type("image/webp")).to_be_false()


def test_accepts_mime_type_preserves_literal_wildcard_semantics():
    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "image/jpeg"},
    )
    request = RequestParameters(request=tornado_request)
    context = SimpleNamespace(request=request)
    handler = make_handler(context)

    expect(handler.accepts_mime_type("image/jpeg")).to_be_true()
    expect(handler.accepts_mime_type("*/*")).to_be_false()


def test_accepts_mime_type_super_call_uses_parsed_quality():
    class CustomHandler(BaseHandler):
        def accepts_mime_type(  # pylint: disable=useless-parent-delegation
            self, mimetype=""
        ):
            return super().accepts_mime_type(mimetype)

    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "image/avif;q=0,image/*;q=0.8"},
    )
    request = RequestParameters(request=tornado_request)
    request.engine = engine
    context = SimpleNamespace(
        config=Config(AUTO_AVIF=True),
        request=request,
    )
    handler = make_handler(context, CustomHandler)

    expect(handler.accepts_mime_type("image/avif")).to_be_false()
    expect(handler.can_auto_convert_to_avif()).to_be_false()


def test_accepts_mime_type_super_call_honors_image_wildcard():
    class CustomHandler(BaseHandler):
        def accepts_mime_type(  # pylint: disable=useless-parent-delegation
            self, mimetype=""
        ):
            return super().accepts_mime_type(mimetype)

    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "image/*;q=0.8"},
    )
    request = RequestParameters(request=tornado_request)
    request.engine = engine
    context = SimpleNamespace(
        config=Config(AUTO_AVIF=True),
        request=request,
    )
    handler = make_handler(context, CustomHandler)

    expect(handler.accepts_mime_type("image/avif")).to_be_true()
    expect(handler.accepts_mime_type("application/json")).to_be_false()
    expect(handler.accepts_mime_type("*/*")).to_be_false()
    expect(handler.can_auto_convert_to_avif()).to_be_true()
