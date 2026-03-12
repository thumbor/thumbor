# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import optparse
import sys
from io import StringIO
from unittest import TestCase, mock

import thumbor.url_composer as composer
from thumbor.url_composer import (
    get_options,
    get_parser,
    get_thumbor_params,
    main,
)


class UrlComposerTestCase(TestCase):
    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_can_compose_url(self, mock_stdout):
        main(
            [
                "-k",
                "MY-SECURITY-KEY",
                "-w",
                "200",
                "-e",
                "300",
                "myserver.com/myimg.jpg",
            ]
        )

        assert mock_stdout.getvalue() == (
            "URL:\n/G_dykuWBGyEil5JnNh9cBke0Ajo=/200x300/myserver.com/myimg.jpg\n"
        )

    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch.object(composer.Config, "load")
    def test_fails_when_no_config_or_key(self, load_mock, mock_stdout):
        load_mock.side_effect = RuntimeError("fail to load")

        with self.assertRaises(SystemExit) as system_error:
            main(["-w", "200", "-e", "300", "myserver.com/myimg.jpg"])

        assert mock_stdout.getvalue() == (
            "Error: The -k or --key argument is mandatory. "
            "For more information type thumbor-url -h\n"
        )

        assert system_error.exception.code == 1

    def test_get_thumbor_params(self):
        params = mock.Mock(
            key_file="./tests/fixtures/thumbor.key",
            crop=None,
        )
        config = mock.Mock()

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key == b"SECURITY_KEY_FILE"
        assert thumbor_params["image_url"] == "/image/url.jpg"

    def test_get_thumbor_params_with_crop(self):
        params = mock.Mock(
            key_file="./tests/fixtures/thumbor.key",
            crop="300x200:400x500",
        )
        config = mock.Mock()

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key == b"SECURITY_KEY_FILE"
        assert thumbor_params["image_url"] == "/image/url.jpg"
        assert thumbor_params["crop_left"] == "300"
        assert thumbor_params["crop_top"] == "200"
        assert thumbor_params["crop_right"] == "400"
        assert thumbor_params["crop_bottom"] == "500"

    def test_get_thumbor_params_full_adaptive_fitin_false(self):
        params = mock.Mock(
            key_file=None,
            crop=None,
            fitin=False,
            full=False,
            adaptive=False,
        )
        config = mock.Mock(SECURITY_KEY="woot")

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key is not None
        assert thumbor_params["fit_in"] is False
        assert thumbor_params["full_fit_in"] is False
        assert thumbor_params["adaptive_fit_in"] is False
        assert thumbor_params["adaptive_full_fit_in"] is False

    def test_get_thumbor_params_full_adaptive_fitin(self):
        params = mock.Mock(
            key_file=None,
            crop=None,
            fitin=True,
            full=True,
            adaptive=True,
        )
        config = mock.Mock(SECURITY_KEY="woot")

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key is not None
        assert thumbor_params["adaptive_full_fit_in"] is True

    def test_get_thumbor_params_adaptive_fitin(self):
        params = mock.Mock(
            key_file=None,
            crop=None,
            fitin=True,
            full=False,
            adaptive=True,
        )
        config = mock.Mock(SECURITY_KEY="woot")

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key is not None
        assert thumbor_params["adaptive_fit_in"] is True

    def test_get_thumbor_params_full_fitin(self):
        params = mock.Mock(
            key_file=None,
            crop=None,
            fitin=True,
            full=True,
            adaptive=False,
        )
        config = mock.Mock(SECURITY_KEY="woot")

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key is not None
        assert thumbor_params["full_fit_in"] is True

    def test_get_thumbor_params_fitin(self):
        params = mock.Mock(
            key_file=None,
            crop=None,
            fitin=True,
            full=False,
            adaptive=False,
        )
        config = mock.Mock(SECURITY_KEY="woot")

        security_key, thumbor_params = get_thumbor_params(
            "/image/url.jpg",
            params,
            config,
        )

        assert security_key is not None
        assert thumbor_params["fit_in"] is True

    def test_get_options(self):
        options, args = get_options(
            [
                "-k",
                "MY-SECURITY-KEY",
                "-w",
                "200",
                "-e",
                "300",
                "myserver.com/myimg.jpg",
            ]
        )

        assert options.key == "MY-SECURITY-KEY"
        assert options.width == 200
        assert options.height == 300

        assert len(args) == 1
        assert args[0] == "myserver.com/myimg.jpg"

    def test_get_options_from_sys(self):
        argv = [
            "thumbor-url",
            "-k",
            "MY-SECURITY-KEY",
            "-w",
            "200",
            "-e",
            "300",
            "myserver.com/myimg.jpg",
        ]
        with mock.patch.object(sys, "argv", argv):
            options, args = get_options(None)

        assert options.key == "MY-SECURITY-KEY"
        assert options.width == 200
        assert options.height == 300

        assert len(args) == 1
        assert args[0] == "myserver.com/myimg.jpg"

    def test_get_options_fails_when_no_url(self):
        parsed_options, arguments = get_options(
            ["-k", "MY-SECURITY-KEY", "-w", "200", "-e", "300"]
        )
        assert parsed_options is None
        assert arguments is None

    def test_get_parser(self):
        parser = get_parser()
        assert isinstance(parser, optparse.OptionParser)
        assert parser.get_usage() == (
            "Usage: thumbor-url [options] imageurl or type thumbor-url -h (--help) for help\n"
        )
