#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from json import loads, dumps
from datetime import datetime, timedelta
from hashlib import md5

from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TBufferedTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase
from hbase.ttypes import Mutation

from thumbor.storages import BaseStorage

class Storage(BaseStorage):
    crypto_col = 'crypto'
    detector_col = 'detector'
    image_col = 'raw'

    def __init__(self,context):
        self.context=context
        self.table = self.context.config.HBASE_STORAGE_TABLE
        self.data_fam = self.context.config.HBASE_STORAGE_FAMILLY
        transport = TBufferedTransport(TSocket(host=self.context.config.HBASE_STORAGE_SERVER_HOST, port=self.context.config.HBASE_STORAGE_SERVER_PORT))
        transport.open()
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        self.storage = Hbase.Client(protocol)

    def put(self, path, bytes):
        r = [Mutation(column=self.data_fam + ':' + self.image_col, value=bytes)]
        self.storage.mutateRow(self.table, md5(path).hexdigest() + '-' + path, r)

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.config.SECURITY_KEY:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        r = [Mutation(column=self.data_fam + ':' + self.crypto_col, value=self.context.config.SECURITY_KEY)]
        self.storage.mutateRow(self.table, md5(path).hexdigest() + '-' + path, r)

    def put_detector_data(self, path, data):
        r = [Mutation(column=self.data_fam + ':' + self.detector_col, value=dumps(data))]
        self.storage.mutateRow(self.table, md5(path).hexdigest() + '-' + path, r)

    def get_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return None

        crypto = self.storage.get(self.table, md5(path).hexdigest() + '-' + path, self.data_fam + ':' + self.crypto_col)

        if not crypto:
            return None
        return crypto[0].value

    def get_detector_data(self, path):
        data = self.storage.get(self.table, md5(path).hexdigest() + '-' + path, self.data_fam + ':' + self.detector_col)

        try:
            return loads(data[0].value)
        except IndexError:
            return None

    def get(self, path):
        r = self.storage.get(self.table, md5(path).hexdigest() + '-' + path, self.data_fam + ':' + self.image_col)
        try:
            return r[0].value
        except IndexError: 
          return None
