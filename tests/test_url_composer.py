#!/usr/bin/python
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

from preggy import expect

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

        expect(mock_stdout.getvalue()).to_equal(
            "URL:\n/G_dykuWBGyEil5JnNh9cBke0Ajo=/200x300/myserver.com/myimg.jpg\n"
        )

    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch.object(composer.Config, "load")
    def test_fails_when_no_config_or_key(self, load_mock, mock_stdout):
        load_mock.side_effect = RuntimeError("fail to load")

        with self.assertRaises(SystemExit) as system_error:
            main(["-w", "200", "-e", "300", "myserver.com/myimg.jpg"])

        expect(mock_stdout.getvalue()).to_equal(
            "Error: The -k or --key argument is mandatory. "
            "For more information type thumbor-url -h\n"
        )

        expect(system_error.exception.code).to_equal(1)

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

        expect(security_key).to_equal("SECURITY_KEY_FILE")
        expect(thumbor_params["image_url"]).to_equal("/image/url.jpg")

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

        expect(security_key).to_equal("SECURITY_KEY_FILE")
        expect(thumbor_params["image_url"]).to_equal("/image/url.jpg")
        expect(thumbor_params["crop_left"]).to_equal("300")
        expect(thumbor_params["crop_top"]).to_equal("200")
        expect(thumbor_params["crop_right"]).to_equal("400")
        expect(thumbor_params["crop_bottom"]).to_equal("500")

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

        expect(security_key).not_to_be_null()
        expect(thumbor_params["fit_in"]).to_be_false()
        expect(thumbor_params["full_fit_in"]).to_be_false()
        expect(thumbor_params["adaptive_fit_in"]).to_be_false()
        expect(thumbor_params["adaptive_full_fit_in"]).to_be_false()

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

        expect(security_key).not_to_be_null()
        expect(thumbor_params["adaptive_full_fit_in"]).to_be_true()

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

        expect(security_key).not_to_be_null()
        expect(thumbor_params["adaptive_fit_in"]).to_be_true()

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

        expect(security_key).not_to_be_null()
        expect(thumbor_params["full_fit_in"]).to_be_true()

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

        expect(security_key).not_to_be_null()
        expect(thumbor_params["fit_in"]).to_be_true()

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

        expect(options.key).to_equal("MY-SECURITY-KEY")
        expect(options.width).to_equal(200)
        expect(options.height).to_equal(300)

        expect(args).to_length(1)
        expect(args[0]).to_equal("myserver.com/myimg.jpg")

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

        expect(options.key).to_equal("MY-SECURITY-KEY")
        expect(options.width).to_equal(200)
        expect(options.height).to_equal(300)

        expect(args).to_length(1)
        expect(args[0]).to_equal("myserver.com/myimg.jpg")

    def test_get_options_fails_when_no_url(self):
        parsed_options, arguments = get_options(
            ["-k", "MY-SECURITY-KEY", "-w", "200", "-e", "300"]
        )
        expect(parsed_options).to_be_null()
        expect(arguments).to_be_null()

    def test_get_parser(self):
        parser = get_parser()
        expect(parser).to_be_instance_of(optparse.OptionParser)
        expect(parser.get_usage()).to_equal(
            "Usage: thumbor-url [options] imageurl or type thumbor-url -h (--help) for help\n"
        )
