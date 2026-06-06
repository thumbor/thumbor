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

from thumbor.threadpool import ThreadPool


@pytest.mark.asyncio
async def test_can_get_threadpool_instance():
    instance = ThreadPool.instance(0)
    assert instance.pool is None

    instance = ThreadPool.instance(10)
    assert instance is not None

    instance2 = ThreadPool.instance(10)
    assert instance2 == instance

    instance3 = ThreadPool.instance(11)
    assert instance3 != instance


@pytest.mark.asyncio
async def test_can_run_task_in_foreground():
    instance = ThreadPool.instance(0)
    assert instance is not None

    def add():
        return 10

    result = await instance._execute_in_foreground(add)
    assert result == 10


@pytest.mark.asyncio
async def test_can_run_task_in_foreground_and_exception_happens():
    instance = ThreadPool.instance(0)
    assert instance is not None
    exception = Exception("Boom")

    def add():
        raise exception

    with pytest.raises(Exception, match="Boom"):
        await instance._execute_in_foreground(add)


@pytest.mark.asyncio
async def test_queueing_task_when_no_pool_runs_sync():
    instance = ThreadPool.instance(0)
    assert instance is not None

    def add():
        return 10

    result = await instance.queue(add)
    assert result == 10


@pytest.mark.asyncio
async def test_queueing_task_when_no_pool_runs_sync_and_exception_happens():
    instance = ThreadPool.instance(0)
    assert instance is not None
    exception = Exception("Boom")

    def add():
        raise exception

    with pytest.raises(Exception, match="Boom"):
        await instance.queue(add)


@pytest.mark.asyncio
async def test_can_run_async():
    instance = ThreadPool.instance(10)
    assert instance is not None

    def add():
        sleep(1)
        return 10

    result = await instance._execute_in_pool(add)
    assert result == 10


@pytest.mark.asyncio
async def test_can_run_async_with_queue():
    instance = ThreadPool.instance(10)
    assert instance is not None

    def add(value):
        sleep(1)
        return value

    result = await instance.queue(add, 10)
    assert result == 10


@pytest.mark.asyncio
async def test_can_cleanup_pool():
    instance = ThreadPool.instance(0)
    instance.pool = mock.Mock()
    instance.cleanup()

    assert instance.pool.shutdown.called
