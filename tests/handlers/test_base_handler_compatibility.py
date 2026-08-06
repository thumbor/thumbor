# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 globo.com thumbor@googlegroups.com

from types import SimpleNamespace
from unittest import mock

import pytest
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


@pytest.mark.parametrize(
    "conversion_method,accepted_mimetype",
    [
        ("can_auto_convert_to_avif", "image/avif"),
        ("can_auto_convert_to_heif", "image/heif"),
        ("can_auto_convert_to_jpg", "image/jpeg"),
        ("can_auto_convert_to_png", "image/png"),
    ],
)
def test_accepts_mime_type_remains_an_extension_point(
    conversion_method, accepted_mimetype
):
    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            return mimetype == accepted_mimetype

    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.has_transparency.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    engine.can_auto_convert_to_heif.return_value = True
    request = SimpleNamespace(
        accepts_avif=False,
        accepts_heif=False,
        accepts_jpeg=False,
        accepts_png=False,
        engine=engine,
        headers=None,
    )
    context = SimpleNamespace(
        config=SimpleNamespace(
            AUTO_AVIF=True,
            AUTO_HEIF=True,
            AUTO_JPG=True,
            AUTO_PNG=True,
        ),
        request=request,
    )
    handler = make_handler(context, CustomHandler)

    expect(getattr(handler, conversion_method)()).to_be_true()


def test_accepts_mime_type_override_can_reject_a_parsed_format():
    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            return False

    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    request = SimpleNamespace(
        accepts_avif=True,
        engine=engine,
        headers={"Accept": "image/avif"},
    )
    context = SimpleNamespace(
        config=SimpleNamespace(AUTO_AVIF=True),
        request=request,
    )
    handler = make_handler(context, CustomHandler)

    expect(handler.can_auto_convert_to_avif()).to_be_false()


@pytest.mark.parametrize(
    "conversion_method,accept_header",
    [
        ("can_auto_convert_to_avif", "image/avif"),
        ("can_auto_convert_to_heif", "image/heif"),
        ("can_auto_convert_to_jpg", "image/jpeg"),
        ("can_auto_convert_to_png", "image/png"),
    ],
)
def test_legacy_request_object_falls_back_to_the_accept_header(
    conversion_method, accept_header
):
    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.has_transparency.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    engine.can_auto_convert_to_heif.return_value = True
    request = SimpleNamespace(
        engine=engine,
        headers={"Accept": accept_header},
    )
    context = SimpleNamespace(
        config=SimpleNamespace(
            AUTO_AVIF=True,
            AUTO_HEIF=True,
            AUTO_JPG=True,
            AUTO_PNG=True,
        ),
        request=request,
    )
    handler = make_handler(context)

    expect(getattr(handler, conversion_method)()).to_be_true()
