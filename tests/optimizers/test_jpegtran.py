#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase, mock

from thumbor.config import Config
from thumbor.context import Context, RequestParameters
from thumbor.optimizers.jpegtran import Optimizer


class JpegtranOptimizerTest(TestCase):
    def setUp(self):
        self.patcher = mock.patch("thumbor.optimizers.jpegtran.Popen")
        self.mock_popen = self.patcher.start()
        self.os_path_exists_patcher = mock.patch(
            "thumbor.optimizers.jpegtran.exists"
        )
        self.mock_os_path_exists = self.os_path_exists_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.os_path_exists_patcher.stop()

    @staticmethod
    def get_optimizer(filters=None, progressive=False, scans_file=""):
        conf = Config()
        conf.STATSD_HOST = ""
        conf.JPEGTRAN_PATH = "/somewhere/jpegtran"
        conf.PROGRESSIVE_JPEG = progressive
        conf.JPEGTRAN_SCANS_FILE = scans_file
        req = RequestParameters(filters=filters)
        ctx = Context(config=conf)
        ctx.request = req
        optimizer = Optimizer(ctx)

        return optimizer

    def test_should_run_for_jpeg(self):
        optimizer = self.get_optimizer()
        self.assertTrue(optimizer.should_run(".jpg", ""))
        self.assertTrue(optimizer.should_run(".jpeg", ""))

    def test_should_not_run_for_not_jpeg(self):
        optimizer = self.get_optimizer()

        self.assertFalse(optimizer.should_run(".png", ""))
        self.assertFalse(optimizer.should_run(".webp", ""))
        self.assertFalse(optimizer.should_run(".gif", ""))

    def test_should_not_run_if_binary_jpegtran_path_does_not_exist(self):
        self.mock_os_path_exists.return_value = False

        optimizer = self.get_optimizer()
        self.assertFalse(optimizer.should_run(".jpg", ""))

    def test_should_optimize(self):
        input_buffer = "input buffer"
        output_buffer = "output buffer"
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            output_buffer,
            "Error",
        )

        optimizer = self.get_optimizer()
        return_buffer = optimizer.run_optimizer(".jpg", input_buffer)

        self.mock_popen.return_value.communicate.assert_called_with(
            input_buffer
        )
        self.assertEqual(output_buffer, return_buffer)

    def test_should_return_old_buffer_for_invalid_extension(self):
        optimizer = self.get_optimizer()
        buffer = "garbage"

        return_buffer = optimizer.run_optimizer(".png", buffer)

        self.assertEqual(return_buffer, buffer)

    def test_should_return_old_buffer_for_invalid_image(self):
        optimizer = self.get_optimizer()
        buffer = "garbage"

        self.mock_popen.return_value.returncode = 1
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        return_buffer = optimizer.run_optimizer(".jpg", buffer)

        self.assertEqual(return_buffer, buffer)

    def test_should_preserve_comments_if_strip_icc_filter_set(self):
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        optimizer = self.get_optimizer(filters=["strip_icc"])
        optimizer.run_optimizer(".jpg", "")

        command = self.mock_popen.call_args[0][0]

        self.assertIn("-copy", command)
        self.assertIn("comments", command)
        self.assertNotIn("all", command)

        optimizer = self.get_optimizer()
        optimizer.run_optimizer(".jpg", "")

        command = self.mock_popen.call_args[0][0]

        self.assertIn("-copy", command)
        self.assertIn("all", command)
        self.assertNotIn("comments", command)

    def test_should_make_progressive_when_configured(self):
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        optimizer = self.get_optimizer(progressive=False)
        optimizer.run_optimizer(".jpg", "")

        args, _ = self.mock_popen.call_args
        command = args[0]

        self.assertNotIn("-progressive", command)

        optimizer = self.get_optimizer(progressive=True)
        optimizer.run_optimizer(".jpg", "")

        args, _ = self.mock_popen.call_args
        command = args[0]

        self.assertIn("-progressive", command)

    def test_should_not_use_scans_file_when_not_configured(self):
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        optimizer = self.get_optimizer(scans_file="")
        optimizer.run_optimizer(".jpg", "")

        args, _ = self.mock_popen.call_args
        command = args[0]

        self.assertNotIn("-scans", command)

    def test_should_use_scans_file_when_configured_and_exists(self):
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        self.mock_os_path_exists.return_value = True

        optimizer = self.get_optimizer(scans_file="scans_test.txt")
        optimizer.run_optimizer(".jpg", "")

        args, _ = self.mock_popen.call_args
        command = args[0]

        self.assertIn("-scans", command)
        self.assertIn("scans_test.txt", command)

    @mock.patch("thumbor.optimizers.jpegtran.logger.warning")
    def test_should_log_warning_when_scans_file_missing(self, warn_logger):
        self.mock_popen.return_value.returncode = 0
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        self.mock_os_path_exists.side_effect = (
            lambda filename: filename != "scans_test.txt"
        )

        optimizer = self.get_optimizer(scans_file="scans_test.txt")
        optimizer.run_optimizer(".jpg", "")

        args, _ = self.mock_popen.call_args
        command = args[0]

        self.assertNotIn("-scans", command)
        warn_logger.assert_called_once()

    @mock.patch("thumbor.optimizers.jpegtran.logger.warning")
    def test_should_log_warning_when_failed(self, warn_logger):
        optimizer = self.get_optimizer()

        self.mock_popen.return_value.returncode = 1
        self.mock_popen.return_value.communicate.return_value = (
            "Output",
            "Error",
        )

        optimizer.run_optimizer(".jpg", "garbage")

        warn_logger.assert_called_once()
