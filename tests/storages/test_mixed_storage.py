# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from collections import defaultdict

import tornado

from tests.base import TestCase
from thumbor.context import ServerParameters
from thumbor.importer import Importer
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.storages.no_storage import Storage as NoStorage


class Storage:
    def __init__(self, security_key):
        self.storage = defaultdict(dict)
        self.security_key = security_key

    async def put(self, path, contents):
        self.storage[path]["path"] = path
        self.storage[path]["contents"] = contents

    async def put_crypto(self, path):
        self.storage[path]["crypto"] = self.security_key

    async def put_detector_data(self, path, data):
        self.storage[path]["detector"] = data

    async def get_crypto(self, path):
        if path not in self.storage:
            raise RuntimeError(f"{path} was not found in storage")

        return self.storage[path]["crypto"]

    async def get_detector_data(self, path):
        if path not in self.storage or "detector" not in self.storage[path]:
            return None

        return self.storage[path]["detector"]

    async def get(self, path):
        if path not in self.storage:
            raise RuntimeError(f"{path} was not found in storage")

        return self.storage[path]["contents"]


class BasedMixedStorageTestCase(TestCase):
    def __init__(self, *args, **kw):
        self.context = None
        self.storage = None
        super().__init__(*args, **kw)

    def get_storages(self):
        return (
            Storage("security-key"),
            Storage("security-key"),
            Storage("detector"),
        )

    def get_context(self):
        context = super().get_context()
        self.storage = MixedStorage(None, *self.get_storages())
        return context

    def get_server(self):
        server = ServerParameters(
            8888, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return server

    def get_importer(self):
        return Importer(self.config)


class MixedStorageTestCase(BasedMixedStorageTestCase):
    @tornado.testing.gen_test
    async def test_mixed_storage_put_includes_path(self):
        await self.storage.put("path1", "contents")
        await self.storage.put_crypto("path1")
        await self.storage.put_detector_data("path1", "detector")

        assert self.storage.file_storage.storage["path1"]["path"] == "path1"
        assert self.storage.file_storage.storage["path1"]["contents"] == (
            "contents"
        )

        contents = await self.storage.get("path1")
        assert contents == "contents"
        assert "crypto" not in self.storage.file_storage.storage["path1"]
        assert "contents" not in self.storage.crypto_storage.storage["path1"]
        assert self.storage.crypto_storage.storage["path1"]["crypto"] == (
            "security-key"
        )

        contents = await self.storage.get_crypto("path1")
        assert contents == "security-key"

        contents = await self.storage.get_detector_data("path1")
        assert contents == "detector"


class MixedStorageFromConfTestCase(BasedMixedStorageTestCase):
    def get_context(self):
        context = super().get_context()
        self.storage = MixedStorage(context)
        return context

    @tornado.testing.gen_test
    async def test_get_data(self):
        path = await self.storage.get("path")
        _, _, _ = self.get_storages()
        assert isinstance(self.storage.file_storage, NoStorage)
        assert path is None

    @tornado.testing.gen_test
    async def test_get_detector_data(self):
        path = await self.storage.get_detector_data("path")
        assert isinstance(self.storage.detector_storage, NoStorage)
        assert path is None

    @tornado.testing.gen_test
    async def test_get_crypto(self):
        path = await self.storage.get_crypto("path")
        assert isinstance(self.storage.crypto_storage, NoStorage)
        assert path is None
