#se!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TBufferedTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase, ttypes


from pyvows import Vows, expect

from thumbor.storages.hbase_storage import Storage
from thumbor.context import Context
from thumbor.config import Config
from fixtures.storage_fixture import IMAGE_URL, IMAGE_BYTES, get_server

class HbaseDBContext(Vows.Context):
    def setup(self):
        transport = TBufferedTransport(TSocket(host='localhost', port=9090))
        transport.open()
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.connection = Hbase.Client(protocol)
        self.table='thumbor-test'
        self.family='images:'

        columns = []
        col = ttypes.ColumnDescriptor()
        col.name = self.family
        col.maxVersions = 1
        columns.append(col)
        try:
            self.connection.disableTable(self.table)
            self.connection.deleteTable(self.table)
        except ttypes.IOError:
            pass
	self.connection.createTable(self.table, columns)

@Vows.batch
class HbaseStorageVows(HbaseDBContext):
    class CanStoreImage(Vows.Context):
        def topic(self):
            config = Config(HBASE_STORAGE_TABLE=self.parent.table,HBASE_STORAGE_SERVER_PORT=9090,SECURITY_KEY='ACME-SEC')
            storage = Storage(Context(config=config, server=get_server('ACME-SEC')))
            storage.put(IMAGE_URL % 1, IMAGE_BYTES)
            return self.parent.connection.get(self.parent.table,IMAGE_URL % 1,self.parent.family)

        def should_be_in_catalog(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

    class CanGetImage(Vows.Context):
        def topic(self):
            config = Config(HBASE_STORAGE_TABLE=self.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
            storage = Storage(Context(config=config, server=get_server('ACME-SEC')))

            storage.put(IMAGE_URL % 2, IMAGE_BYTES)
            return storage.get(IMAGE_URL % 2)

        def should_not_be_null(self, topic):
            expect(topic).not_to_be_null()
            expect(topic).not_to_be_an_error()

        def should_have_proper_bytes(self, topic):
            expect(topic).to_equal(IMAGE_BYTES)

    class CanGetImageExistance(Vows.Context):
        def topic(self):
            config = Config(HBASE_STORAGE_TABLE=self.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
            storage = Storage(Context(config=config, server=get_server('ACME-SEC')))

            storage.put(IMAGE_URL % 8, IMAGE_BYTES)
            return storage.exists(IMAGE_URL % 8)

        def should_exists(self, topic):
            expect(topic).to_equal(True)

    class CanGetImageInexistance(Vows.Context):
        def topic(self):
            config = Config(HBASE_STORAGE_TABLE=self.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
            storage = Storage(Context(config=config, server=get_server('ACME-SEC')))

            return storage.exists(IMAGE_URL % 9999)

        def should_not_exists(self, topic):
            expect(topic).to_equal(False)

    class CanRemoveImage(Vows.Context):
        def topic(self):
            config = Config(HBASE_STORAGE_TABLE=self.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
            storage = Storage(Context(config=config, server=get_server('ACME-SEC')))

            storage.put(IMAGE_URL % 9, IMAGE_BYTES)
            created = storage.exists(IMAGE_URL % 9)
            storage.remove(IMAGE_URL % 9)
            return storage.exists(IMAGE_URL % 9) != created

        def should_be_put_and_removed(self, topic):
            expect(topic).to_equal(True)


    class CryptoVows(Vows.Context):
        class RaisesIfInvalidConfig(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090, SECURITY_KEY='', STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = Storage(Context(config=config, server=get_server('')))
                storage.put(IMAGE_URL % 3, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 3)

            def should_be_an_error(self, topic):
                expect(topic).to_be_an_error_like(RuntimeError)
                expect(topic).to_have_an_error_message_of("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        class GettingCryptoForANewImageReturnsNone(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090, STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = Storage(Context(config=config, server=get_server('ACME-SEC')))
                return storage.get_crypto(IMAGE_URL % 9999)

            def should_be_null(self, topic):
                expect(topic).to_be_null()

        class DoesNotStoreIfConfigSaysNotTo(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
                storage = Storage(Context(config=config, server=get_server('ACME-SEC')))
                storage.put(IMAGE_URL % 5, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 5)
                return storage.get_crypto(IMAGE_URL % 5)

            def should_be_null(self, topic):
                expect(topic).to_be_null()

        class CanStoreCrypto(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090, SECURITY_KEY='ACME-SEC', STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True)
                storage = Storage(Context(config=config, server=get_server('ACME-SEC')))

                storage.put(IMAGE_URL % 6, IMAGE_BYTES)
                storage.put_crypto(IMAGE_URL % 6)
                return storage.get_crypto(IMAGE_URL % 6)

            def should_not_be_null(self, topic):
                expect(topic).not_to_be_null()
                expect(topic).not_to_be_an_error()

            def should_have_proper_key(self, topic):
                expect(topic).to_equal('ACME-SEC')

    class DetectorVows(Vows.Context):
        class CanStoreDetectorData(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
                storage = Storage(Context(config=config, server=get_server('ACME-SEC')))
                storage.put(IMAGE_URL % 7, IMAGE_BYTES)
                storage.put_detector_data(IMAGE_URL % 7, 'some-data')
                return storage.get_detector_data(IMAGE_URL % 7)

            def should_not_be_null(self, topic):
                expect(topic).not_to_be_null()
                expect(topic).not_to_be_an_error()

            def should_equal_some_data(self, topic):
                expect(topic).to_equal('some-data')

        class ReturnsNoneIfNoDetectorData(Vows.Context):
            def topic(self):
                config = Config(HBASE_STORAGE_TABLE=self.parent.parent.table,HBASE_STORAGE_SERVER_PORT=9090)
                storage = Storage(Context(config=config, server=get_server('ACME-SEC')))
                return storage.get_detector_data(IMAGE_URL % 10000)

            def should_not_be_null(self, topic):
                expect(topic).to_be_null()

