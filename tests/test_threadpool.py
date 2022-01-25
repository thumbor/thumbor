#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# pylint: disable=protected-access

from time import sleep
from unittest import mock

import pytest
from preggy import expect

from thumbor.threadpool import ThreadPool


@pytest.mark.asyncio
async def test_can_get_threadpool_instance():
    instance = ThreadPool.instance(0)
    expect(instance.pool).to_be_null()

    instance = ThreadPool.instance(10)
    expect(instance).not_to_be_null()

    instance2 = ThreadPool.instance(10)
    expect(instance2).to_equal(instance)

    instance3 = ThreadPool.instance(11)
    expect(instance3).not_to_equal(instance)


@pytest.mark.asyncio
async def test_can_run_task_in_foreground():
    instance = ThreadPool.instance(0)
    expect(instance).not_to_be_null()

    def add():
        return 10

    result = await instance._execute_in_foreground(add)
    expect(result).to_equal(10)


@pytest.mark.asyncio
async def test_can_run_task_in_foreground_and_exception_happens():
    instance = ThreadPool.instance(0)
    expect(instance).not_to_be_null()
    exception = Exception("Boom")

    def add():
        raise exception

    with expect.error_to_happen(Exception, message="Boom"):
        await instance._execute_in_foreground(add)


@pytest.mark.asyncio
async def test_queueing_task_when_no_pool_runs_sync():
    instance = ThreadPool.instance(0)
    expect(instance).not_to_be_null()

    def add():
        return 10

    result = await instance.queue(add)
    expect(result).to_equal(10)


@pytest.mark.asyncio
async def test_queueing_task_when_no_pool_runs_sync_and_exception_happens():
    instance = ThreadPool.instance(0)
    expect(instance).not_to_be_null()
    exception = Exception("Boom")

    def add():
        raise exception

    with expect.error_to_happen(Exception, message="Boom"):
        await instance.queue(add)


@pytest.mark.asyncio
async def test_can_run_async():
    instance = ThreadPool.instance(10)
    expect(instance).not_to_be_null()

    def add():
        sleep(1)
        return 10

    result = await instance._execute_in_pool(add)
    expect(result).to_equal(10)


@pytest.mark.asyncio
async def test_can_run_async_with_queue():
    instance = ThreadPool.instance(10)
    expect(instance).not_to_be_null()

    def add(value):
        sleep(1)
        return value

    result = await instance.queue(add, 10)
    expect(result).to_equal(10)


@pytest.mark.asyncio
async def test_can_cleanup_pool():
    instance = ThreadPool.instance(0)
    instance.pool = mock.Mock()
    instance.cleanup()

    expect(instance.pool.shutdown.called).to_be_true()
