#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
from unittest import TestCase, mock

from preggy import expect

import thumbor.server
from tests.fixtures.custom_error_handler import (
    ErrorHandler as CustomErrorHandler,
)
from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.server import (
    configure_log,
    get_application,
    get_as_integer,
    get_config,
    get_context,
    get_importer,
    main,
    run_server,
    validate_config,
)


class ServerTestCase(TestCase):
    def test_can_get_value_as_integer(self):
        expect(get_as_integer("1")).to_equal(1)
        expect(get_as_integer("a")).to_be_null()
        expect(get_as_integer("")).to_be_null()
        expect(get_as_integer(None)).to_be_null()

    def test_can_get_config_from_path(self):
        config = get_config("./tests/fixtures/thumbor_config_server_test.conf")

        with mock.patch.dict("os.environ", {"ENGINE": "test"}):
            expect(config).not_to_be_null()
            expect(config.ALLOWED_SOURCES).to_be_like(["mydomain.com"])
            expect(config.ENGINE).to_be_like("thumbor.engines.pil")

    def test_can_get_config_with_env_enabled(self):
        config = get_config(
            "./tests/fixtures/thumbor_config_server_test.conf", True
        )

        with mock.patch.dict("os.environ", {"ENGINE": "test"}):
            expect(config).not_to_be_null()
            expect(config.ALLOWED_SOURCES).to_be_like(["mydomain.com"])
            expect(config.ENGINE).to_be_like("test")

    @mock.patch("logging.basicConfig")
    def test_can_configure_log_from_config(self, basic_config_mock):
        conf = Config()
        configure_log(conf, "DEBUG")

        params = {
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "level": 10,
            "format": "%(asctime)s %(name)s:%(levelname)s %(message)s",
        }

        basic_config_mock.assert_called_with(**params)

    @mock.patch("logging.config.dictConfig")
    def test_can_configure_log_from_dict_config(self, dict_config_mock):
        conf = Config(THUMBOR_LOG_CONFIG={"level": "INFO"})
        configure_log(conf, "DEBUG")

        params = {
            "level": "INFO",
        }

        dict_config_mock.assert_called_with(params)

    def test_can_import_default_modules(self):
        conf = Config()
        importer = get_importer(conf)

        expect(importer).not_to_be_null()
        expect(importer.filters).not_to_be_empty()

    def test_can_import_with_custom_error_handler_class(self):
        conf = Config(
            USE_CUSTOM_ERROR_HANDLING=True,
            ERROR_HANDLER_MODULE="tests.fixtures.custom_error_handler",
        )
        importer = get_importer(conf)

        expect(importer).not_to_be_null()
        expect(importer.error_handler_class).not_to_be_null()
        expect(importer.error_handler_class).to_be_instance_of(
            CustomErrorHandler
        )

    def test_validate_config_security_key(self):
        server_parameters = mock.Mock(security_key=None)
        conf = Config(SECURITY_KEY=None)

        with expect.error_to_happen(
            RuntimeError,
            message="No security key was found for this instance of thumbor. "
            "Please provide one using the conf file or a security key file.",
        ):
            validate_config(conf, server_parameters)

    def test_validate_config_security_key_from_config(self):
        server_parameters = mock.Mock(security_key=None)
        conf = Config(SECURITY_KEY="something")

        validate_config(conf, server_parameters)
        expect(server_parameters.security_key).to_equal("something")

    @mock.patch.object(thumbor.server, "which")
    def test_validate_gifsicle_path(self, which_mock):
        server_parameters = mock.Mock(security_key=None)
        conf = Config(SECURITY_KEY="test", USE_GIFSICLE_ENGINE=True)

        which_mock.return_value = "/usr/bin/gifsicle"

        validate_config(conf, server_parameters)
        expect(server_parameters.gifsicle_path).to_equal("/usr/bin/gifsicle")

    @mock.patch.object(thumbor.server, "which")
    def test_validate_null_gifsicle_path(self, which_mock):
        server_parameters = mock.Mock(security_key=None)
        conf = Config(SECURITY_KEY="test", USE_GIFSICLE_ENGINE=True)

        which_mock.return_value = None

        with expect.error_to_happen(
            RuntimeError,
            message="If using USE_GIFSICLE_ENGINE configuration to True, "
            "the `gifsicle` binary must be in the PATH and must be an executable.",
        ):
            validate_config(conf, server_parameters)

    def test_get_context(self):
        server_parameters = mock.Mock(
            security_key=None, app_class="thumbor.app.ThumborServiceApp"
        )
        conf = Config(SECURITY_KEY="test")
        importer = get_importer(conf)
        context = get_context(server_parameters, conf, importer)

        expect(context).not_to_be_null()

    def test_get_application(self):
        server_parameters = mock.Mock(
            security_key=None, app_class="thumbor.app.ThumborServiceApp"
        )
        conf = Config(SECURITY_KEY="test")
        importer = get_importer(conf)
        context = get_context(server_parameters, conf, importer)
        app = get_application(context)

        expect(app).not_to_be_null()
        expect(app).to_be_instance_of(ThumborServiceApp)

    @mock.patch.object(thumbor.server, "HTTPServer")
    def test_can_run_server_with_default_params(self, server_mock):
        application = mock.Mock()
        context = mock.Mock()
        context.server = mock.Mock(
            fd=None, port=1234, ip="0.0.0.0", processes=1
        )

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        run_server(application, context)

        server_instance_mock.bind.assert_called_with(1234, "0.0.0.0")
        server_instance_mock.start.assert_called_with(1)

    @mock.patch.object(thumbor.server, "HTTPServer")
    def test_can_run_server_with_multiple_processes(self, server_mock):
        application = mock.Mock()
        context = mock.Mock()
        context.server = mock.Mock(
            fd=None, port=1234, ip="0.0.0.0", processes=5
        )

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        run_server(application, context)

        server_instance_mock.start.assert_called_with(5)

    @mock.patch.object(thumbor.server, "HTTPServer")
    @mock.patch.object(thumbor.server, "socket", autospec=True)
    def test_can_run_server_with_fd(self, socket_mock, server_mock):
        application = mock.Mock()
        context = mock.Mock()
        context.server = mock.Mock(fd=11, port=1234, ip="0.0.0.0", processes=1)

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        run_server(application, context)
        socket_mock.assert_called_with(fileno=11)
        server_instance_mock.add_socket.assert_called_with(
            socket_mock.return_value
        )
        server_instance_mock.start.assert_called_with(1)

    @mock.patch.object(thumbor.server, "HTTPServer")
    @mock.patch.object(thumbor.server, "socket", autospec=True)
    def test_can_run_server_with_fd_non_blocking(
        self, socket_mock, server_mock
    ):
        server_parameters = mock.Mock(security_key=None)
        conf = Config(SECURITY_KEY="test", NON_BLOCKING_SOCKETS=True)
        importer = get_importer(conf)
        context = get_context(server_parameters, conf, importer)

        context.server = mock.Mock(fd=11, port=1234, ip="0.0.0.0", processes=1)

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        application = mock.Mock()
        run_server(application, context)
        socket_mock.assert_called_with(fileno=11)
        socket_mock.return_value.setblocking.assert_called_with(False)
        server_instance_mock.add_socket.assert_called_with(
            socket_mock.return_value
        )
        server_instance_mock.start.assert_called_with(1)

    @mock.patch.object(thumbor.server, "HTTPServer")
    @mock.patch.object(thumbor.server, "bind_unix_socket")
    def test_can_run_server_with_unix_socket(
        self, bind_unix_socket, server_mock
    ):
        application = mock.Mock()
        context = mock.Mock()
        context.server = mock.Mock(
            fd="/path/bin", port=1234, ip="0.0.0.0", processes=1
        )

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        bind_unix_socket.return_value = "socket mock"

        run_server(application, context)

        bind_unix_socket.assert_called_with("/path/bin")
        server_instance_mock.add_socket.assert_called_with("socket mock")
        server_instance_mock.start.assert_called_with(1)

    @mock.patch.object(thumbor.server, "HTTPServer")
    def test_run_server_returns_server(self, server_mock):
        application = mock.Mock()
        context = mock.Mock()
        context.server = mock.Mock(fd=None, port=1234, ip="0.0.0.0")

        server_instance_mock = mock.Mock()
        server_mock.return_value = server_instance_mock

        server = run_server(application, context)

        self.assertEqual(server, server_instance_mock)

    @mock.patch.object(thumbor.server, "setup_signal_handler")
    @mock.patch.object(thumbor.server, "HTTPServer")
    @mock.patch.object(thumbor.server, "get_server_parameters")
    @mock.patch("tornado.ioloop.IOLoop.instance", create=True)
    def test_can_run_main(
        self,
        ioloop_mock,
        get_server_parameters_mock,
        server_mock,
        setup_signal_handler_mock,
    ):
        server_parameters = mock.Mock(
            config_path="./tests/fixtures/thumbor_config_server_test.conf",
            log_level="DEBUG",
            debug=False,
            security_key="sec",
            app_class="thumbor.app.ThumborServiceApp",
            fd=None,
            ip="0.0.0.0",
            port=1234,
        )
        get_server_parameters_mock.return_value = server_parameters

        ioloop_instance_mock = mock.Mock()
        ioloop_mock.return_value = ioloop_instance_mock
        main()
        ioloop_instance_mock.start.assert_any_call()
        self.assertTrue(setup_signal_handler_mock.called)
        self.assertTrue(server_mock.called)

    def cleanup(self):
        ServerTestCase.cleanup_called = True
