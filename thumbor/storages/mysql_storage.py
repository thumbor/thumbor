#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from datetime import datetime

from tornado.options import options, define
import MySQLdb as mysql

from thumbor.storages import BaseStorage

define('MYSQL_STORAGE_SERVER_HOST', type=str, default='localhost')
define('MYSQL_STORAGE_SERVER_PORT', type=int, default=3306)
define('MYSQL_STORAGE_SERVER_USER', type=str, default='root')
define('MYSQL_STORAGE_SERVER_PASSWORD', type=str, default='')
define('MYSQL_STORAGE_SERVER_DB', type=str, default='thumbor')
define('MYSQL_STORAGE_SERVER_TABLE', type=str, default='images')

class Storage(BaseStorage):

    def __conn__(self):
        return mysql.connect(host=options.MYSQL_STORAGE_SERVER_HOST,
                             user=options.MYSQL_STORAGE_SERVER_USER,
                             passwd=options.MYSQL_STORAGE_SERVER_PASSWORD,
                             db=options.MYSQL_STORAGE_SERVER_DB)


    def put(self, path, bytes):
        connection = self.__conn__()
        try:
            sql = "INSERT INTO images(url, contents, security_key) VALUES(%s, %s, %s)"

            security_key = ''
            if options.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
                if not options.SECURITY_KEY:
                    raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")
                security_key = options.SECURITY_KEY

            cursor = connection.cursor()
            cursor.execute(sql, (path, bytes, security_key))
        finally:
            connection.close()

    def get_crypto(self, path):
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
        return timediff.seconds > options.STORAGE_EXPIRATION_SECONDS

