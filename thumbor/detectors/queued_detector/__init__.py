#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from redis import Redis, RedisError, Sentinel
from remotecv.unique_queue import UniqueQueue

from thumbor.detectors import BaseDetector
from thumbor.utils import logger

SINGLE_NODE = "single_node"
SENTINEL = "sentinel"


class QueuedDetector(BaseDetector):
    queue = None
    detection_type = "all"

    async def detect(self):
        self.context.request.prevent_result_storage = True
        try:
            if not QueuedDetector.queue:
                redis = self.redis_client()
                QueuedDetector.queue = UniqueQueue(server=redis)

            QueuedDetector.queue.enqueue_unique_from_string(
                "remotecv.pyres_tasks.DetectTask",
                "Detect",
                args=[self.detection_type, self.context.request.image_url],
                key=self.context.request.image_url,
            )
        except RedisError:
            self.context.request.detection_error = True
            QueuedDetector.queue = None
            logger.exception("Redis Error")

        # Error or not we return an empty list as detection
        # will be done later
        return []

    def redis_client(self):
        redis_mode = str(self.context.config.REDIS_QUEUE_MODE).lower()

        if redis_mode == SINGLE_NODE:
            return self.__redis_single_node_client()
        if redis_mode == SENTINEL:
            return self.__redis_sentinel_client()

        raise RedisError(
            f"REDIS_QUEUE_MODE must be {SINGLE_NODE} or {SENTINEL}"
        )

    def __redis_single_node_client(self):
        return Redis(
            host=self.context.config.REDIS_QUEUE_SERVER_HOST,
            port=self.context.config.REDIS_QUEUE_SERVER_PORT,
            db=self.context.config.REDIS_QUEUE_SERVER_DB,
            password=self.context.config.REDIS_QUEUE_SERVER_PASSWORD,
        )

    def __redis_sentinel_client(self):
        instances_split = (
            self.context.config.REDIS_QUEUE_SENTINEL_INSTANCES.split(",")
        )
        instances = [
            tuple(instance.split(":")) for instance in instances_split
        ]

        if self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
                sentinel_kwargs={
                    "password": self.context.config.REDIS_QUEUE_SENTINEL_PASSWORD
                },
            )
        else:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
            )

        return sentinel_instance.master_for(
            self.context.config.REDIS_QUEUE_SENTINEL_MASTER_INSTANCE,
            socket_timeout=self.context.config.REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT,
            password=self.context.config.REDIS_QUEUE_SENTINEL_MASTER_PASSWORD,
            db=self.context.config.REDIS_QUEUE_SENTINEL_MASTER_DB,
        )
