# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2026 Marcelo Jorge Vieira <metal@alucinados.com>

import hmac

REALM = "thumbor-upload"


def split_tokens(value):
    if isinstance(value, str):
        return [token.strip() for token in value.split(",")]

    if isinstance(value, (list, tuple, set, frozenset)):
        return [
            token.strip() if isinstance(token, str) else token
            for token in value
        ]

    return None


def is_valid_token(token):
    return (
        isinstance(token, str)
        and token != ""
        and token.isascii()
        and not any(character.isspace() for character in token)
    )


def get_valid_tokens(value):
    return [
        token.encode("ascii")
        for token in split_tokens(value) or []
        if is_valid_token(token)
    ]


def get_bearer_credentials(header):
    scheme, _, credentials = (header or "").partition(" ")
    credentials = credentials.strip()

    if scheme.lower() != "bearer" or not credentials:
        return None

    # Tokens are ASCII, so any other character only has to be encodable to
    # be rejected by the comparison instead of raising.
    return credentials.encode("utf-8", "surrogatepass")


def is_authorized(credentials, tokens):
    authorized = False
    for token in tokens:
        authorized |= hmac.compare_digest(credentials, token)
    return authorized
