#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from unittest import TestCase
import mock
from json import loads, dumps
import hashlib

from preggy import expect
import pylibmc

from thumbor.storages.memcache_storage import (
    Storage
)


class MemcacheStorageTestCase(TestCase):
    def setUp(self, *args, **kw):
        super(MemcacheStorageTestCase, self).setUp(*args, **kw)
        self.memcached = pylibmc.Client(
            ['localhost:5555'],
            binary=True,
            behaviors={
                'tcp_nodelay': True,
                'no_block': True,
                'ketama': True
            }
        )

        self.memcached.flush_all()

        self.context = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                STORAGE_EXPIRATION_SECONDS=120,
            )
        )

    def test_can_create_storage(self):
        storage = Storage(self.context)
        expect(storage).not_to_be_null()

    def test_can_get_key_for_url(self):
        storage = Storage(self.context)
        url = 'http://www.globo.com/'
        expected = hashlib.sha1(url).hexdigest()
        expect(storage.key_for(url)).to_equal(expected)

    def test_can_get_crypto_key_for_url(self):
        storage = Storage(self.context)
        key = 'thumbor-crypto-http://www.globo.com/'
        expected = hashlib.sha1(key).hexdigest()
        expect(storage.crypto_key_for('http://www.globo.com/')).to_equal(expected)

    def test_can_get_detector_key_for_url(self):
        storage = Storage(self.context)
        key = 'thumbor-detector-http://www.globo.com/'
        expected = hashlib.sha1(key).hexdigest()
        expect(storage.detector_key_for('http://www.globo.com/')).to_equal(expected)

    def test_can_put_data(self):
        storage = Storage(self.context)

        key = '/some/path/to/file.jpg'
        storage.put(key, 'test-data')

        data = self.memcached.get(storage.key_for(key))
        expect(data).to_equal('test-data')

    def test_can_put_detector_data(self):
        storage = Storage(self.context)

        key = '/some/path/to/file.jpg'
        storage.put_detector_data(key, 'detector-test-data')

        data = self.memcached.get(storage.detector_key_for(key))
        expect(loads(data)).to_equal('detector-test-data')

    def test_put_crypto_when_not_storing_crypto_for_each_image(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                STORAGE_EXPIRATION_SECONDS=120,
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=False,
            )
        )

        storage = Storage(ctx)
        storage.put_crypto('/some/path/to/file.jpg')

        data = self.memcached.get('thumbor-crypto-/some/path/to/file.jpg')
        expect(data).to_be_null()

    def test_put_crypto_raises_when_no_security_key(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                STORAGE_EXPIRATION_SECONDS=120,
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
            ),
            server=mock.Mock(
                security_key=None
            ),
        )

        storage = Storage(ctx)

        expected_msg = 'STORES_CRYPTO_KEY_FOR_EACH_IMAGE can\'t be True if no SECURITY_KEY specified'
        with expect.error_to_happen(RuntimeError, message=expected_msg):
            storage.put_crypto('/some/path/to/file.jpg')

    def test_put_crypto_when_valid_data(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                STORAGE_EXPIRATION_SECONDS=120,
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
            ),
            server=mock.Mock(
                security_key='some-key'
            ),
        )

        storage = Storage(ctx)

        storage.put_crypto('/some/path/to/file.jpg')
        data = self.memcached.get(storage.crypto_key_for('/some/path/to/file.jpg'))
        expect(data).to_equal('some-key')

    def test_can_get_image(self):
        key = '/some/path/to/file.jpg'
        storage = Storage(self.context)
        self.memcached.set(storage.key_for(key), 'test-data')

        data = storage.get(key).result()
        expect(data).to_equal('test-data')

    def test_can_get_crypto(self):
        key = '/some/path/to/file.jpg'
        storage = Storage(self.context)
        self.memcached.set(storage.crypto_key_for(key), 'test-crypto-data')

        data = storage.get_crypto(key).result()
        expect(data).to_equal('test-crypto-data')

    def test_get_crypto_when_not_storing_crypto_for_each_image(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                STORAGE_EXPIRATION_SECONDS=120,
                STORES_CRYPTO_KEY_FOR_EACH_IMAGE=False,
            )
        )

        storage = Storage(ctx)
        data = storage.get_crypto('/some/path/to/file.jpg').result()
        expect(data).to_be_null()

    def test_can_get_detector_data(self):
        key = '/some/path/to/file.jpg'
        storage = Storage(self.context)
        self.memcached.set(storage.detector_key_for(key), dumps('test-detector-data'))

        data = storage.get_detector_data(key).result()
        expect(data).to_equal('test-detector-data')

    def test_can_verify_if_path_exists(self):
        storage = Storage(self.context)
        key = '/some/path/to/file.jpg'

        expect(storage.exists(key).result()).to_be_false()

        self.memcached.set(storage.key_for(key), 'test-data')
        expect(storage.exists(key).result()).to_be_true()

    def test_can_remove_from_storage(self):
        storage = Storage(self.context)
        key = '/some/path/to/file.jpg'

        # does not fail even if key not found
        storage.remove(key)

        expect(storage.exists(key).result()).to_be_false()

        self.memcached.set(storage.key_for(key), 'test-data')

        storage.remove(key)

        expect(storage.exists(key).result()).to_be_false()

    # Regression test for #309 - Has support for memcached been dropped?
    def test_can_verify_if_path_exists_for_unicode_path(self):
        storage = Storage(self.context)
        key = u'/some/path/to/téste.jpg'

        expect(storage.exists(key).result()).to_be_false()
        self.memcached.set(storage.key_for(key), 'test-data')
        expect(storage.exists(key).result()).to_be_true()
