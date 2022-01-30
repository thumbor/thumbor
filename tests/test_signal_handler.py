#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import signal
from unittest import TestCase, mock

from thumbor.signal_handler import setup_signal_handler, signal_handler


class SignalhandlerTestCase(TestCase):
    @mock.patch("thumbor.signal_handler.signal")
    def test_setup_signal_handler_sets_handler(self, signal_mock):
        signal_mock.SIGINT = 2
        signal_mock.SIGTERM = 15
        setup_signal_handler(mock.Mock(), mock.Mock())

        signal_mock.signal.assert_has_calls(
            [
                mock.call(signal_mock.SIGTERM, mock.ANY),
                mock.call(signal_mock.SIGINT, mock.ANY),
            ]
        )

    @mock.patch("tornado.ioloop.IOLoop.instance", create=True)
    def test_signal_handler_calls_add_callback_from_signal(self, ioloop_mock):
        ioloop_instance_mock = mock.Mock()
        ioloop_mock.return_value = ioloop_instance_mock

        signal_handler(mock.Mock(), mock.Mock(), signal.SIGTERM, mock.Mock())

        ioloop_instance_mock.add_callback_from_signal.assert_called_with(
            mock.ANY
        )
