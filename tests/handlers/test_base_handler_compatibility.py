# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 globo.com thumbor@googlegroups.com

import datetime
from types import SimpleNamespace
from unittest import mock

import pytest
from preggy import expect

from thumbor.auto_image_format import get_auto_image_format_cache_key
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


def make_jpeg_handler(accept_header):
    class CustomHandler(BaseHandler):
        def accepts_mime_type(  # pylint: disable=useless-parent-delegation
            self, mimetype=""
        ):
            return super().accepts_mime_type(mimetype)

    engine = mock.Mock()
    engine.is_multiple.return_value = False
    engine.has_transparency.return_value = False
    tornado_request = mock.Mock(
        path="/image.png",
        headers={"Accept": accept_header},
    )
    request = RequestParameters(request=tornado_request)
    request.engine = engine
    context = SimpleNamespace(config=Config(AUTO_JPG=True), request=request)
    return make_handler(context, CustomHandler)


def test_is_webp_keeps_legacy_behavior():
    context = make_context()
    handler = make_handler(context)

    expect(handler.is_webp(context)).to_be_true()

    context.config.AUTO_WEBP = False
    expect(handler.is_webp(context)).to_be_false()


def test_can_auto_convert_to_webp_keeps_is_webp_extension_point():
    class CustomHandler(BaseHandler):
        def is_webp(self, context):
            return True

    context = make_context(auto_webp=False)
    handler = make_handler(context, CustomHandler)

    expect(handler.can_auto_convert_to_webp()).to_be_true()


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

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()
    expect(get_auto_image_format_cache_key(context.config, request)).to_equal(
        "auto_format_v1_flags_preserve_avif"
    )


@pytest.mark.parametrize(
    "accept_header",
    [
        "image/jpeg;q=0,*/*;q=0.8",
        "image/jpg;q=0,*/*;q=0.8",
        "image/*;q=0,*/*;q=0.8",
        "image/jpeg;q=0,image/jpg;q=0.8",
    ],
)
def test_custom_accepts_mime_type_honors_explicit_jpeg_rejection(
    accept_header,
):
    handler = make_jpeg_handler(accept_header)

    expect(handler.context.request.accepts_jpeg).to_be_false()
    expect(handler.can_auto_convert_to_jpg()).to_be_false()

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()
    expect(
        get_auto_image_format_cache_key(
            handler.context.config, handler.context.request
        )
    ).to_equal("auto_format_v1_flags_preserve_default")


@pytest.mark.parametrize(
    "accept_header",
    [
        "*/*;q=0.8",
        "image/jpeg;q=0.8,image/*;q=0",
    ],
)
def test_custom_accepts_mime_type_keeps_valid_jpeg_fallback(accept_header):
    handler = make_jpeg_handler(accept_header)

    expect(handler.can_auto_convert_to_jpg()).to_be_true()

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()
    expect(
        get_auto_image_format_cache_key(
            handler.context.config, handler.context.request
        )
    ).to_equal("auto_format_v1_flags_preserve_jpg")


def test_custom_accepts_mime_type_bypasses_result_storage_without_calling_it():
    calls = []

    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            calls.append(mimetype)
            return "*/*" in self.context.request.headers.get("Accept", "")

    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "*/*"},
    )
    request = RequestParameters(request=tornado_request)
    config = Config(AUTO_AVIF=True)
    context = SimpleNamespace(config=config, request=request)
    handler = make_handler(context, CustomHandler)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()

    request.headers = {"Accept": ""}
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()
    expect(calls).to_be_empty()


def test_custom_accepts_mime_type_runs_after_engine_is_available():
    calls = []

    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            calls.append(mimetype)
            return self.context.request.engine.accepts_mime_type(mimetype)

    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "image/avif"},
    )
    request = RequestParameters(request=tornado_request)
    context = SimpleNamespace(
        config=Config(AUTO_AVIF=True),
        request=request,
    )
    handler = make_handler(context, CustomHandler)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()

    expect(calls).to_be_empty()

    engine = mock.Mock()
    engine.accepts_mime_type.return_value = True
    engine.is_multiple.return_value = False
    engine.can_auto_convert_to_avif.return_value = True
    request.engine = engine

    expect(handler.can_auto_convert_to_avif()).to_be_true()
    expect(calls).to_equal(["image/avif"])


@pytest.mark.parametrize(
    "config_overrides",
    [
        {"AUTO_AVIF": True},
        {"AUTO_HEIF": True},
        {"AUTO_JPG": True},
        {"AUTO_PNG": True},
        {"AUTO_IMAGE_FORMAT_PREFERENCE": ["webp", "jpg"]},
    ],
)
def test_custom_accepts_mime_type_bypasses_extended_format_cache(
    config_overrides,
):
    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            return True

    context = SimpleNamespace(
        config=Config(**config_overrides),
        request=RequestParameters(),
    )
    handler = make_handler(context, CustomHandler)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()


@pytest.mark.parametrize(
    "config_overrides,expected_cache_key",
    [
        ({"AUTO_WEBP": True}, "auto_webp"),
        (
            {"AUTO_IMAGE_FORMAT_PREFERENCE": ["webp"]},
            "auto_format_v1_preference_preserve_webp",
        ),
        (
            {"AUTO_PNG_TO_JPG": True},
            "auto_format_v1_flags_png_to_jpg_default",
        ),
    ],
)
def test_custom_accepts_mime_type_keeps_webp_cache(
    config_overrides,
    expected_cache_key,
):
    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            return True

    request = RequestParameters(accepts_webp=True)
    context = SimpleNamespace(
        config=Config(**config_overrides),
        request=request,
    )
    handler = make_handler(context, CustomHandler)
    handler.accepts_mime_type = mock.Mock(return_value=True)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_true()

    handler.accepts_mime_type.assert_not_called()
    expect(get_auto_image_format_cache_key(context.config, request)).to_equal(
        expected_cache_key
    )


@pytest.mark.asyncio
async def test_custom_accepts_mime_type_bypasses_result_storage_read_and_write():
    calls = []

    class CustomHandler(BaseHandler):
        def accepts_mime_type(self, mimetype=""):
            calls.append(mimetype)
            return self.context.request.engine.accepts_mime_type(mimetype)

    tornado_request = mock.Mock(
        path="/image.jpg",
        headers={"Accept": "image/avif"},
    )
    request = RequestParameters(request=tornado_request)
    result_storage = mock.AsyncMock()
    result_storage.get.return_value = None
    filters_runner = SimpleNamespace(apply_filters=mock.AsyncMock())
    filters_factory = mock.Mock()
    filters_factory.create_instances.return_value = filters_runner
    thread_pool = SimpleNamespace(
        queue=mock.AsyncMock(return_value=(b"image", "image/jpeg"))
    )
    context = SimpleNamespace(
        config=Config(AUTO_AVIF=True),
        request=request,
        modules=SimpleNamespace(result_storage=result_storage),
        metrics=mock.Mock(),
        filters_factory=filters_factory,
        thread_pool=thread_pool,
    )
    handler = make_handler(context, CustomHandler)
    handler._response_start = (  # pylint: disable=protected-access
        datetime.datetime.now()
    )
    handler.request = SimpleNamespace(arguments={})
    handler.get_image = mock.AsyncMock()

    await handler.execute_image_operations()

    result_storage.get.assert_not_awaited()
    handler.get_image.assert_awaited_once_with()
    expect(calls).to_be_empty()

    handler._write_results_to_client = (  # pylint: disable=protected-access
        mock.AsyncMock()
    )
    handler._cleanup = mock.Mock()  # pylint: disable=protected-access

    await handler.finish_request()

    result_storage.put.assert_not_awaited()
    expect(request.prevent_result_storage).to_be_false()


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


def test_legacy_request_object_bypasses_result_storage():
    context = SimpleNamespace(
        config=Config(AUTO_AVIF=True),
        request=SimpleNamespace(headers={"Accept": "image/avif"}),
    )
    handler = make_handler(context)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_false()


def test_legacy_request_object_keeps_result_storage_with_webp_only():
    context = SimpleNamespace(
        config=Config(AUTO_WEBP=True),
        request=SimpleNamespace(headers={"Accept": "image/webp"}),
    )
    handler = make_handler(context)

    # pylint: disable=protected-access
    expect(
        handler._can_use_result_storage_with_auto_image_formats()
    ).to_be_true()
