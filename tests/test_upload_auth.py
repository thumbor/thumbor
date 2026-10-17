# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import pytest

from thumbor.upload_auth import (
    get_bearer_credentials,
    get_valid_tokens,
    is_authorized,
    is_valid_token,
    split_tokens,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ([], []),
        ((), []),
        (["first", " second "], ["first", "second"]),
        (("first",), ["first"]),
        ({"first"}, ["first"]),
        ("first", ["first"]),
        (" first , second ", ["first", "second"]),
        ("first,,second", ["first", "", "second"]),
        ("", [""]),
        ([123, b"first"], [123, b"first"]),
    ],
)
def test_split_tokens(value, expected):
    assert split_tokens(value) == expected


@pytest.mark.parametrize("value", [None, 123, b"first", {"first": 1}])
def test_split_tokens_rejects_other_types(value):
    assert split_tokens(value) is None


@pytest.mark.parametrize("token", ["a", "first-token", "ABC_def.123~+/="])
def test_is_valid_token_accepts_ascii_without_whitespace(token):
    assert is_valid_token(token)


@pytest.mark.parametrize(
    "token",
    [
        "",
        "with space",
        "with\ttab",
        "line\nbreak",
        "tok\u00e9n",
        None,
        123,
        b"x",
    ],
)
def test_is_valid_token_rejects_invalid_tokens(token):
    assert not is_valid_token(token)


def test_get_valid_tokens_encodes_and_skips_invalid_tokens():
    assert get_valid_tokens(["first", "", "tok\u00e9n", 123, "second"]) == [
        b"first",
        b"second",
    ]


@pytest.mark.parametrize("value", [None, 123, [], ""])
def test_get_valid_tokens_without_valid_tokens(value):
    assert get_valid_tokens(value) == []


@pytest.mark.parametrize(
    "header,expected",
    [
        ("Bearer token", b"token"),
        ("bearer token", b"token"),
        ("BEARER token", b"token"),
        ("Bearer   token  ", b"token"),
        ("Bearer tok\u00e9n", "tok\u00e9n".encode("utf-8")),
        ("Bearer \ud800", b"\xed\xa0\x80"),
    ],
)
def test_get_bearer_credentials(header, expected):
    assert get_bearer_credentials(header) == expected


@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "Bearer",
        "Bearer ",
        "Basic dXNlcjpwYXNz",
        "token",
        "Bearertoken",
    ],
)
def test_get_bearer_credentials_without_bearer_credentials(header):
    assert get_bearer_credentials(header) is None


def test_is_authorized_accepts_any_configured_token():
    tokens = [b"first", b"second"]

    assert is_authorized(b"first", tokens)
    assert is_authorized(b"second", tokens)


@pytest.mark.parametrize(
    "credentials", [b"third", b"firs", b"first ", b"", "tok\u00e9n".encode()]
)
def test_is_authorized_rejects_other_credentials(credentials):
    assert not is_authorized(credentials, [b"first", b"second"])


def test_is_authorized_without_tokens():
    assert not is_authorized(b"first", [])
