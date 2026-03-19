# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import importlib
from importlib import metadata
from unittest import TestCase, mock

from preggy import expect

import thumbor


class VersionTestCase(TestCase):
    def tearDown(self):
        importlib.reload(thumbor)

    def test_prefers_installed_package_metadata(self):
        with mock.patch(
            "importlib.metadata.version", return_value="9.9.9"
        ) as version_mock:
            module = importlib.reload(thumbor)

        expect(module.__version__).to_equal("9.9.9")
        expect(version_mock.called).to_be_true()

    def test_falls_back_to_unknown_version(self):
        with mock.patch(
            "importlib.metadata.version",
            side_effect=metadata.PackageNotFoundError("thumbor"),
        ) as version_mock:
            module = importlib.reload(thumbor)

        expect(module.__version__).to_equal("0+unknown")
        expect(version_mock.called).to_be_true()
