#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from collections import defaultdict
from typing import Any, Dict, Optional, Tuple

import tornado
from preggy import expect

from thumbor.context import ServerParameters
from thumbor.importer import Importer
from thumbor.storages import BaseStorage
from thumbor.storages.mixed_storage import Storage as MixedStorage
from thumbor.storages.no_storage import Storage as NoStorage
from thumbor.testing import TestCase


class Storage(BaseStorage):
    def __init__(self, security_key: str):
        self.storage: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.security_key: str = security_key

    async def put(self, path: str, contents: bytes) -> Optional[str]:
        self.storage[path]["path"] = path
        self.storage[path]["contents"] = contents.decode("utf-8")
        return path

    async def put_crypto(self, path: str) -> Optional[str]:
        self.storage[path]["crypto"] = self.security_key
        return path

    async def put_detector_data(self, path: str, data: str) -> Optional[str]:
        self.storage[path]["detector"] = data
        return path

    async def get_crypto(self, path: str) -> Optional[str]:
        if path not in self.storage:
            raise RuntimeError("%s was not found in storage" % path)

        return self.storage[path]["crypto"]

    async def get_detector_data(self, path: str) -> Optional[str]:
        if path not in self.storage or "detector" not in self.storage[path]:
            return None

        return self.storage[path]["detector"]

    async def get(self, path: str) -> Optional[bytes]:
        if path not in self.storage:
            raise RuntimeError("%s was not found in storage" % path)

        return self.storage[path]["contents"].encode("utf-8")


class BasedMixedStorageTestCase(TestCase):
    def __init__(self, *args, **kw):
        self.context: Any = None
        self.storage: BaseStorage = None
        super(BasedMixedStorageTestCase, self).__init__(*args, **kw)

    def get_storages(self) -> Tuple[BaseStorage, ...]:
        return (
            Storage("security-key"),
            Storage("security-key"),
            Storage("detector"),
        )

    def get_context(self) -> Any:
        context = super(BasedMixedStorageTestCase, self).get_context()
        self.storage = MixedStorage(None, *self.get_storages())
        return context

    def get_server(self) -> ServerParameters:
        server = ServerParameters(8888, "localhost", "thumbor.conf", None, "info", None)
        server.security_key = "ACME-SEC"
        return server

    def get_importer(self) -> Importer:
        return Importer(self.config)


class MixedStorageTestCase(BasedMixedStorageTestCase):
    @tornado.testing.gen_test
    async def test_mixed_storage_put_includes_path(self):
        await self.storage.initialize(self.context)
        await self.storage.put("path1", b"contents")
        await self.storage.put_crypto("path1")
        await self.storage.put_detector_data("path1", "detector")

        expect(self.storage.file_storage.storage["path1"]["path"]).to_equal("path1")
        expect(self.storage.file_storage.storage["path1"]["contents"]).to_equal(
            "contents"
        )

        contents = await self.storage.get("path1")
        expect(contents).to_equal("contents")
        expect(self.storage.file_storage.storage["path1"]).not_to_include("crypto")
        expect(self.storage.crypto_storage.storage["path1"]).not_to_include("contents")
        expect(self.storage.crypto_storage.storage["path1"]["crypto"]).to_equal(
            "security-key"
        )

        contents = await self.storage.get_crypto("path1")
        expect(contents).to_equal("security-key")

        contents = await self.storage.get_detector_data("path1")
        expect(contents).to_equal("detector")


class MixedStorageFromConfTestCase(BasedMixedStorageTestCase):
    def get_context(self) -> Any:
        context = super(MixedStorageFromConfTestCase, self).get_context()
        self.storage = MixedStorage(context)
        return context

    @tornado.testing.gen_test
    async def test_get_data(self):
        await self.storage.initialize(self.context)
        path = await self.storage.get("path")
        _, _, _ = self.get_storages()
        expect(self.storage.file_storage).to_be_instance_of(NoStorage)
        expect(path).to_be_null()

    @tornado.testing.gen_test
    async def test_get_detector_data(self):
        await self.storage.initialize(self.context)
        path = await self.storage.get_detector_data("path")
        expect(self.storage.detector_storage).to_be_instance_of(NoStorage)
        expect(path).to_be_null()

    @tornado.testing.gen_test
    async def test_get_crypto(self):
        await self.storage.initialize(self.context)
        path = await self.storage.get_crypto("path")
        expect(self.storage.crypto_storage).to_be_instance_of(NoStorage)
        expect(path).to_be_null()
