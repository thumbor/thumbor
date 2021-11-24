#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from concurrent.futures import ThreadPoolExecutor

from tornado.ioloop import IOLoop

from thumbor.utils import logger


class ThreadPool:
    @classmethod
    def instance(cls, size):
        """
        Cache threadpool since context is
        recreated for each request
        """
        if not getattr(cls, "_instance", None):
            cls._instance = {}
        if size not in cls._instance:
            cls._instance[size] = ThreadPool(size)
        return cls._instance[size]

    @classmethod
    def reset(cls):
        if cls._instance is not None:
            for instance in cls._instance.values():
                instance.cleanup()
        cls._instance = None

    def __init__(self, thread_pool_size):
        if thread_pool_size:
            self.pool = ThreadPoolExecutor(thread_pool_size)
        else:
            self.pool = None

    async def _execute_in_foreground(self, operation, *args):
        return operation(*args)

    async def _execute_in_pool(self, operation, *args):
        loop = IOLoop.current()
        return await loop.run_in_executor(self.pool, operation, *args)

    async def queue(self, operation, *args):
        if not self.pool:
            return await self._execute_in_foreground(operation, *args)

        return await self._execute_in_pool(operation, *args)

    def cleanup(self):
        if self.pool:
            logger.info("Shutting down threads")
            self.pool.shutdown()
