#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime

import MySQLdb as mysql

from thumbor.storages import BaseStorage
from thumbor.config import conf

class Storage(BaseStorage):

    def __conn__(self):
        return mysql.connect(host=conf.MYSQL_STORAGE_SERVER_HOST,
                             user=conf.MYSQL_STORAGE_SERVER_USER,
                             passwd=conf.MYSQL_STORAGE_SERVER_PASSWORD,
                             db=conf.MYSQL_STORAGE_SERVER_DB)


    def put(self, path, bytes):
        connection = self.__conn__()
        try:
            sql = "INSERT INTO images(url, contents) VALUES(%s, %s)"

            security_key = ''
            if conf.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
                if not conf.SECURITY_KEY:
                    raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
                security_key = conf.SECURITY_KEY

            cursor = connection.cursor()
            cursor.execute(sql, (path, bytes, security_key))
        finally:
            connection.close()

    def put_crypto(self, path):
        if not conf.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        connection = self.__conn__()
        try:
            security_key = ''
            if not conf.SECURITY_KEY:
                raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
            security_key = conf.SECURITY_KEY

            sql = "UPDATE images set security_key=%s WHERE path=%s"

            cursor = connection.cursor()
            cursor.execute(sql, (security_key, path))
        finally:
            connection.close()

    def get_crypto(self, path):
        if not conf.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return None

        connection = self.__conn__()
        try:
            sql = "SELECT security_key FROM images where url=%s"

            cursor = connection.cursor()
            cursor.execute(sql, path)
            image = cursor.fetchone()

            return image[0] if image else ''
        finally:
            connection.close()

    def get(self, path):
        connection = self.__conn__()
        try:
            sql = "SELECT contents, last_update FROM images where url=%s"

            cursor = connection.cursor()
            cursor.execute(sql, path)
            image = cursor.fetchone()

            if not image or self.__is_expired(image[1]):
                return None

            return image[0]
        finally:
            connection.close()

    def __is_expired(self, last_update):
        timediff = datetime.now() - last_update
        return timediff.seconds > conf.STORAGE_EXPIRATION_SECONDS

