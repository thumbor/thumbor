#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from mock import Mock, patch
from unittest import TestCase
import logging

from preggy import expect

from thumbor.utils import (
    CONTENT_TYPE, EXTENSION,
    logger,
    on_exception,
    deprecated,
    which,
)


class UtilsTestCase(TestCase):
    def setUp(self, *args, **kw):
        self.handled = False
        super(UtilsTestCase, self).setUp(*args, **kw)

    def test_can_get_content_type(self):
        expect(CONTENT_TYPE.get('.jpg')).to_equal('image/jpeg')
        expect(CONTENT_TYPE.get('.jpeg')).to_equal('image/jpeg')
        expect(CONTENT_TYPE.get('.gif')).to_equal('image/gif')
        expect(CONTENT_TYPE.get('.png')).to_equal('image/png')
        expect(CONTENT_TYPE.get('.webp')).to_equal('image/webp')
        expect(CONTENT_TYPE.get('.mp4')).to_equal('video/mp4')
        expect(CONTENT_TYPE.get('.webm')).to_equal('video/webm')
        expect(CONTENT_TYPE.get('.svg')).to_equal('image/svg+xml')
        expect(CONTENT_TYPE.get('.tif')).to_equal('image/tiff')
        expect(CONTENT_TYPE.get('.tiff')).to_equal('image/tiff')

    def test_can_get_extension(self):
        expect(EXTENSION.get('image/jpeg')).to_equal('.jpg')
        expect(EXTENSION.get('image/gif')).to_equal('.gif')
        expect(EXTENSION.get('image/png')).to_equal('.png')
        expect(EXTENSION.get('image/webp')).to_equal('.webp')
        expect(EXTENSION.get('video/mp4')).to_equal('.mp4')
        expect(EXTENSION.get('video/webm')).to_equal('.webm')
        expect(EXTENSION.get('image/svg+xml')).to_equal('.svg')
        expect(EXTENSION.get('image/tiff')).to_equal('.tif')

    def test_can_get_logger(self):
        expect(logger.name).to_equal('thumbor')

    def test_can_create_on_exception(self):
        callback_mock = Mock()
        inst = on_exception(callback_mock)

        expect(inst.callback).to_equal(callback_mock)
        expect(inst.exception_class).to_equal(Exception)

        inst = on_exception(callback_mock, RuntimeError)
        expect(inst.exception_class).to_equal(RuntimeError)

    def test_can_handle_exceptions(self):
        self.handled = False

        def handle_callback(func, exc, exc_value):
            expect(func).to_equal('test_func')
            expect(exc).to_equal(Exception)
            expect(str(exc_value)).to_equal("Test")
            self.handled = True

        @on_exception(handle_callback)
        def test_func():
            raise RuntimeError("Test")

        test_func()
        expect(self.handled).to_be_true()

    def __can_handle_callback(self, func, exc, exc_value):
        expect(func).to_equal('test_func')
        expect(exc).to_equal(Exception)
        expect(str(exc_value)).to_equal("Test")
        self.handled = True

    def test_can_handle_exceptions_with_instance(self):
        self.handled = False

        @on_exception(UtilsTestCase.__can_handle_callback)
        def test_func(self):
            raise RuntimeError("Test")

        test_func(self)
        expect(self.handled).to_be_true()

    def test_cant_handle_exceptions_without_callback(self):
        @on_exception(None)
        def test_func(self):
            raise RuntimeError("Test")

        with expect.error_to_happen(RuntimeError):
            test_func(self)

    def test_deprecated_logs_msg(self):
        @deprecated('func2')
        def test_func():
            pass

        with patch.object(logger, 'warn') as mock_warn:
            test_func()
            mock_warn.assert_called_once_with('Deprecated function test_func: func2')

    def test_can_which_by_path(self):
        result = which('/bin/ls')
        expect(result).to_equal('/bin/ls')

        result = which('/tmp')
        expect(result).to_be_null()

    def test_can_which_by_env(self):
        result = which('ls')
        expect(result).to_equal('/bin/ls')

        result = which('invalid-command')
        expect(result).to_be_null()

    def test_logger_should_be_instance_of_python_logger(self):
        expect(logger).to_be_instance_of(logging.Logger)

    def test_logger_should_not_be_null(self):
        expect(logger).not_to_be_null()

    def test_logger_should_not_be_an_error(self):
        expect(logger).not_to_be_an_error()
