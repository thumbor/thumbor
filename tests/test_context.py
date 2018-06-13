#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
from time import sleep
from unittest import TestCase

import mock
from preggy import expect
from tornado.testing import AsyncTestCase

from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.filters import FiltersFactory
from thumbor.metrics.logger_metrics import Metrics
from thumbor.context import (
    Context, ThreadPool, ServerParameters, RequestParameters,
    ContextImporter,
)


class ContextTestCase(TestCase):
    def test_can_create_context(self):
        ctx = Context()

        expect(ctx.server).to_be_null()
        expect(ctx.config).to_be_null()
        expect(ctx.modules).to_be_null()

        expect(ctx.metrics).not_to_be_null()
        expect(ctx.metrics).to_be_instance_of(Metrics)

        expect(ctx.filters_factory).to_be_instance_of(FiltersFactory)
        expect(ctx.filters_factory.filter_classes_map).to_be_empty()
        expect(ctx.request_handler).to_be_null()
        expect(ctx.thread_pool).to_be_instance_of(ThreadPool)
        expect(ctx.headers).to_be_instance_of(dict)
        expect(ctx.headers).to_be_empty()

    def test_can_create_context_with_importer(self):
        cfg = Config()
        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(config=cfg, importer=importer)

        expect(ctx.modules).not_to_be_null()
        expect(ctx.modules.importer).to_equal(importer)

    def test_can_create_context_without_importer_metrics(self):
        cfg = Config(
            METRICS='',
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer)

        expect(ctx.modules).not_to_be_null()
        expect(ctx.modules.importer).to_equal(importer)

    def test_can_config_define_app_class(self):
        server = ServerParameters(
            port=8888,
            ip='0.0.0.0',
            config_path='/tmp/config_path.conf',
            keyfile='./tests/fixtures/thumbor.key',
            log_level='debug',
            app_class='thumbor.app.ThumborServiceApp',
        )

        cfg = Config(
            APP_CLASS='config.app',
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer, server=server)

        expect(ctx.app_class).to_equal('config.app')

    def test_can_server_app_class_override_config(self):
        server = ServerParameters(
            port=8888,
            ip='0.0.0.0',
            config_path='/tmp/config_path.conf',
            keyfile='./tests/fixtures/thumbor.key',
            log_level='debug',
            app_class='server.app',
        )

        cfg = Config(
            APP_CLASS='config.app',
        )
        importer = Importer(cfg)
        ctx = Context(config=cfg, importer=importer, server=server)

        expect(ctx.app_class).to_equal('server.app')


class ServerParametersTestCase(TestCase):
    def test_can_create_server_parameters(self):
        params = ServerParameters(
            port=8888,
            ip='0.0.0.0',
            config_path='/tmp/config_path.conf',
            keyfile='./tests/fixtures/thumbor.key',
            log_level='debug',
            app_class='app',
            fd='fd',
            gifsicle_path='gifsicle_path',
        )

        expect(params.port).to_equal(8888)
        expect(params.ip).to_equal('0.0.0.0')
        expect(params.config_path).to_equal('/tmp/config_path.conf')
        expect(params.keyfile).to_equal('./tests/fixtures/thumbor.key')
        expect(params.log_level).to_equal('debug')
        expect(params.app_class).to_equal('app')
        expect(params._security_key).to_equal('SECURITY_KEY_FILE')
        expect(params.fd).to_equal('fd')
        expect(params.gifsicle_path).to_equal('gifsicle_path')

        expect(params.security_key).to_equal('SECURITY_KEY_FILE')

    def test_can_set_security_key(self):
        params = ServerParameters(
            port=8888,
            ip='0.0.0.0',
            config_path='/tmp/config_path.conf',
            keyfile='./tests/fixtures/thumbor.key',
            log_level='debug',
            app_class='app',
            fd='fd',
            gifsicle_path='gifsicle_path',
        )

        params.security_key = u'testé'
        expect(params._security_key).to_equal(u'testé'.encode('utf-8'))

    def test_loading_does_nothing_if_no_keyfile(self):
        params = ServerParameters(
            port=8888,
            ip='0.0.0.0',
            config_path='/tmp/config_path.conf',
            keyfile=None,
            log_level='debug',
            app_class='app',
            fd='fd',
            gifsicle_path='gifsicle_path',
        )

        expect(params._security_key).to_be_null()

    def test_cant_load_invalid_security_key_file(self):
        expected_msg = 'Could not find security key file at /bogus. Please verify the keypath argument.'
        with expect.error_to_happen(ValueError, message=expected_msg):
            ServerParameters(
                port=8888,
                ip='0.0.0.0',
                config_path='/tmp/config_path.conf',
                keyfile='/bogus',
                log_level='debug',
                app_class='app',
                fd='fd',
                gifsicle_path='gifsicle_path',
            )


class RequestParametersTestCase(TestCase):
    def test_can_create_request_parameters(self):
        params = RequestParameters()

        expect(params.debug).to_be_false()
        expect(params.meta).to_be_false()
        expect(params.trim).to_be_null()
        expect(params.crop).to_be_like({
            'top': 0,
            'right': 0,
            'bottom': 0,
            'left': 0
        })
        expect(params.should_crop).to_be_false()

        expect(params.adaptive).to_be_false()
        expect(params.full).to_be_false()
        expect(params.adaptive).to_be_false()

        expect(params.width).to_equal(0)
        expect(params.height).to_equal(0)

        expect(params.horizontal_flip).to_be_false()
        expect(params.vertical_flip).to_be_false()

        expect(params.halign).to_equal('center')
        expect(params.valign).to_equal('middle')

        expect(params.smart).to_be_false()

        expect(params.filters).to_be_empty()
        expect(params.image_url).to_be_null()
        expect(params.url).to_be_null()
        expect(params.detection_error).to_be_null()
        expect(params.quality).to_equal(80)
        expect(params.buffer).to_be_null()

        expect(params.focal_points).to_be_empty()

        expect(params.hash).to_be_null()
        expect(params.prevent_result_storage).to_be_false()
        expect(params.unsafe).to_be_false()
        expect(params.format).to_be_null()
        expect(params.accepts_webp).to_be_false()
        expect(params.max_bytes).to_be_null()
        expect(params.max_age).to_be_null()

    def test_can_get_params_with_trim(self):
        params = RequestParameters(trim="trim")
        expect(params.trim_pos).to_equal("top-left")
        expect(params.trim_tolerance).to_equal(0)

    def test_can_get_params_with_trim_with_custom_pos(self):
        params = RequestParameters(trim="trim:bottom-right:10")
        expect(params.trim_pos).to_equal("bottom-right")
        expect(params.trim_tolerance).to_equal(10)

    def test_can_get_params_with_crop(self):
        params = RequestParameters(
            crop_left=10,
            crop_right=20,
            crop_top=30,
            crop_bottom=40,
        )
        expect(params.crop).to_be_like({
            'top': 30, 'right': 20, 'bottom': 40, 'left': 10
        })

    def test_can_get_params_with_custom_crop(self):
        params = RequestParameters(
            crop={
                'top': 30, 'right': 20, 'bottom': 40, 'left': 10
            }
        )
        expect(params.crop).to_be_like({
            'top': 30, 'right': 20, 'bottom': 40, 'left': 10
        })
        expect(params.should_crop).to_be_true()

    def test_can_get_orig_dimensions(self):
        params = RequestParameters(
            width="orig",
            height="orig",
        )
        expect(params.width).to_equal('orig')
        expect(params.height).to_equal('orig')

    def test_can_add_filters(self):
        params = RequestParameters(filters=['a', 'b'])
        expect(params.filters).to_length(2)

    def test_can_add_focal_points(self):
        params = RequestParameters(focal_points=['a', 'b'])
        expect(params.focal_points).to_length(2)

    def test_can_get_params_from_request(self):
        request = mock.Mock(
            path='/test.jpg',
            headers={
                'Accept': 'image/webp',
            }
        )
        params = RequestParameters(request=request, image='/test.jpg')
        expect(params.accepts_webp).to_be_true()
        expect(params.image_url).to_equal('/test.jpg')


class ContextImporterTestCase(TestCase):
    def test_can_create_context_importer(self):
        cfg = Config(
            RESULT_STORAGE='thumbor.result_storages.file_storage',
        )
        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(config=cfg, importer=importer)

        ctx_importer = ContextImporter(ctx, importer)
        expect(ctx_importer.context).to_equal(ctx)
        expect(ctx_importer.importer).to_equal(importer)
        expect(ctx_importer.engine).to_be_instance_of(importer.engine)
        expect(ctx_importer.gif_engine).to_be_instance_of(importer.gif_engine)

        expect(ctx_importer.storage).to_be_instance_of(importer.storage)
        expect(ctx_importer.result_storage).to_be_instance_of(importer.result_storage)
        expect(ctx_importer.upload_photo_storage).to_be_instance_of(importer.upload_photo_storage)

        expect(ctx_importer.loader).to_equal(importer.loader)
        expect(ctx_importer.detectors).to_equal(importer.detectors)
        expect(ctx_importer.filters).to_equal(importer.filters)
        expect(ctx_importer.optimizers).to_equal(importer.optimizers)
        expect(ctx_importer.url_signer).to_equal(importer.url_signer)


class ThreadPoolTestCase(AsyncTestCase):
    def setUp(self):
        super(ThreadPoolTestCase, self).setUp()
        self.handled = False
        ThreadPool._instance = None

    def test_can_get_threadpool_instance(self):
        instance = ThreadPool.instance(0)
        expect(instance.pool).to_be_null()

        instance = ThreadPool.instance(10)
        expect(instance).not_to_be_null()

        instance2 = ThreadPool.instance(10)
        expect(instance2).to_equal(instance)

        instance3 = ThreadPool.instance(11)
        expect(instance3).not_to_equal(instance)

    def test_can_run_task_in_foreground(self):
        instance = ThreadPool.instance(0)
        expect(instance).not_to_be_null()

        def add():
            return 10

        def handle_operation(result):
            self.handled = True
            expect(result.result()).to_equal(10)

        instance._execute_in_foreground(add, handle_operation)
        expect(self.handled).to_be_true()

    def test_can_run_task_in_foreground_and_exception_happens(self):
        instance = ThreadPool.instance(0)
        expect(instance).not_to_be_null()
        exception = Exception('Boom')

        def add():
            raise exception

        def handle_operation(result):
            self.handled = True
            with expect.error_to_happen(Exception, message='Boom'):
                result.result()

        instance._execute_in_foreground(add, handle_operation)
        expect(self.handled).to_be_true()

    def test_queueing_task_when_no_pool_runs_sync(self):
        instance = ThreadPool.instance(0)
        expect(instance).not_to_be_null()

        def add():
            return 10

        def handle_operation(result):
            self.handled = True
            expect(result.result()).to_equal(10)

        instance.queue(add, handle_operation)
        expect(self.handled).to_be_true()

    def test_queueing_task_when_no_pool_runs_sync_and_exception_happens(self):
        instance = ThreadPool.instance(0)
        expect(instance).not_to_be_null()
        exception = Exception('Boom')

        def add():
            raise exception

        def handle_operation(result):
            self.handled = True
            with expect.error_to_happen(Exception, message='Boom'):
                result.result()

        instance.queue(add, handle_operation)
        expect(self.handled).to_be_true()

    def test_can_run_async(self):
        instance = ThreadPool.instance(10)
        expect(instance).not_to_be_null()

        def add():
            sleep(1)
            self.handled = True
            return 10

        instance._execute_in_pool(add, self.stop)
        expect(self.handled).to_be_false()
        result = self.wait()

        expect(self.handled).to_be_true()
        expect(result.result()).to_equal(10)

    def test_can_cleanup_pool(self):
        instance = ThreadPool.instance(0)
        instance.pool = mock.Mock()
        instance.cleanup()

        expect(instance.pool.shutdown.called).to_be_true()
