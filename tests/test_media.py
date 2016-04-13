#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from __future__ import unicode_literals,absolute_import
from unittest import TestCase
import hashlib
import copy
import mock

from preggy import expect

from thumbor.media import Media
from thumbor.result_storages import ResultStorageResult


class MediaTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(MediaTestCase, self).setUp(*args, **kwargs)
        self.buffer_mock = b''


    def test_can_create_empty_media_object(self):
        media = Media()
        expect(media.normalized).to_be_false()
        expect(media.buffer).to_be_null()
        expect(media.engine).to_be_null()
        expect(media.successful).to_be_false()

    def test_can_create_media_object(self):
        result = Media(self.buffer_mock)
        expect(result.buffer).to_equal(self.buffer_mock)
        expect(result.is_valid).to_be_true()

    def test_can_create_media_from_result(self):
        loader_result = ResultStorageResult(buffer=self.buffer_mock)
        loader_result.metadata['ContentType'] = 'image/gif'
        media = Media.from_result(loader_result)
        expect(media.buffer).to_equal(self.buffer_mock)
        expect(media.mime).to_equal('image/gif')

    def test_can_create_media_from_unknown_result(self):
        loader_result = ResultStorageResult(buffer=self.buffer_mock)
        media = Media.from_result(loader_result)
        expect(media.buffer).to_equal(self.buffer_mock)
        expect(media.mime).to_equal('')

        # Try a valid buffer
        loader_result = ResultStorageResult(buffer=b'\x00\x00\x00\x0ctest')
        media = Media.from_result(loader_result)
        expect(media.mime).to_equal('image/jp2')


