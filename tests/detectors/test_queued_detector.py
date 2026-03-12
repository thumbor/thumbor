# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from json import loads
from unittest import mock

from redis import Redis, Sentinel
from tornado.testing import gen_test

from tests.base import DetectorTestCase
from thumbor.config import Config
from thumbor.detectors.queued_detector import QueuedDetector

TEST_REDIS_HOST = "0.0.0.0"
TEST_REDIS_PORT = 6668
TEST_REDIS_PASSWORD = "hey_you"
TEST_REDIS_MODE = "single_node"
TEST_REDIS_SENTINEL_MODE = "sentinel"
TEST_REDIS_QUEUE_SENTINEL_INSTANCES = "localhost:26379"
TEST_REDIS_SENTINEL_MASTER_INSTANCE = "masterinstance"
TEST_REDIS_SENTINEL_SOCKET_TIMEOUT = 10.0


class SharedQueuedDetectorTestCase(DetectorTestCase):
    def setUp(self):
        super().setUp()
        self.redis = None

    async def detector_send_to_queues(self, ctx):
        detector = QueuedDetector(ctx, 1, [])

        data = await detector.detect()
        assert not data
        assert ctx.request.detection_error is False

        result = self.redis.get("resque:unique:queue:Detect:/image/test.jpg")
        assert result == b"1"

        expected_payload = {
            "queue": "Detect",
            "args": ["all", "/image/test.jpg", "/image/test.jpg"],
            "class": "remotecv.pyres_tasks.DetectTask",
            "key": "/image/test.jpg",
        }

        result = self.redis.lpop("resque:queue:Detect")
        assert loads(result.decode("utf-8")) == expected_payload

    async def detector_fails_properly(self, ctx):
        detector = QueuedDetector(ctx, 1, [])

        data = await detector.detect()
        assert not data
        assert ctx.request.detection_error is True
        assert detector.queue is None

    async def detector_can_detect_twice(self, ctx):
        detector = QueuedDetector(ctx, 1, [])

        data = await detector.detect()
        assert not data
        assert ctx.request.detection_error is False
        assert detector.queue is not None

        data = detector.detect()
        assert detector.queue is not None


class QueuedDetectorTestCase(SharedQueuedDetectorTestCase):
    def get_config(self):
        return Config(
            REDIS_QUEUE_SERVER_PORT=TEST_REDIS_PORT,
            REDIS_QUEUE_SERVER_PASSWORD=TEST_REDIS_PASSWORD,
        )

    def setUp(self):
        super().setUp()
        self.redis = Redis(
            host=TEST_REDIS_HOST,
            port=TEST_REDIS_PORT,
            db=0,
            password=TEST_REDIS_PASSWORD,
        )

        self.redis.delete("resque:unique:queue:Detect:/image/test.jpg")
        self.redis.delete("resque:queue:Detect")
        QueuedDetector.queue = None

    @gen_test
    async def test_detector_sends_to_queue(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_MODE=TEST_REDIS_MODE,
                REDIS_QUEUE_SERVER_HOST=TEST_REDIS_HOST,
                REDIS_QUEUE_SERVER_PORT=TEST_REDIS_PORT,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD=TEST_REDIS_PASSWORD,
            ),
            request=mock.Mock(
                image_url="/image/test.jpg",
                detection_error=False,
            ),
        )
        await self.detector_send_to_queues(ctx)

    @gen_test
    async def test_detector_fails_properly(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_MODE=TEST_REDIS_MODE,
                REDIS_QUEUE_SERVER_HOST=TEST_REDIS_HOST,
                REDIS_QUEUE_SERVER_PORT=6669,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD=TEST_REDIS_PASSWORD,
            ),
            request=mock.Mock(
                image_url="/image/test.jpg",
                detection_error=False,
            ),
        )
        await self.detector_fails_properly(ctx)

    @gen_test
    async def test_detector_can_detect_twice(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_MODE=TEST_REDIS_MODE,
                REDIS_QUEUE_SERVER_HOST=TEST_REDIS_HOST,
                REDIS_QUEUE_SERVER_PORT=TEST_REDIS_PORT,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD=TEST_REDIS_PASSWORD,
            ),
            request=mock.Mock(
                image_url="/image/test.jpg",
                detection_error=False,
            ),
        )
        await self.detector_can_detect_twice(ctx)


class QueuedSentinelDetectorTestCase(SharedQueuedDetectorTestCase):
    def get_config(self):
        return Config(
            REDIS_QUEUE_MODE=TEST_REDIS_SENTINEL_MODE,
            REDIS_QUEUE_SENTINEL_PASSWORD=TEST_REDIS_PASSWORD,
            REDIS_QUEUE_SENTINEL_SOCKET_TIMEOUT=TEST_REDIS_SENTINEL_SOCKET_TIMEOUT,
            REDIS_QUEUE_SENTINEL_MASTER_INSTANCE=TEST_REDIS_SENTINEL_MASTER_INSTANCE,
            REDIS_QUEUE_SENTINEL_MASTER_PASSWORD=TEST_REDIS_PASSWORD,
            REDIS_QUEUE_SENTINEL_MASTER_DB=0,
        )

    def setUp(self):
        super().setUp()
        self.sentinel = Sentinel(
            [("localhost", 26379)],
            sentinel_kwargs={"password": TEST_REDIS_PASSWORD},
        )
        self.redis = self.sentinel.master_for(
            TEST_REDIS_SENTINEL_MASTER_INSTANCE,
            password=TEST_REDIS_PASSWORD,
            db=0,
        )

        self.redis.delete("resque:unique:queue:Detect:/image/test.jpg")
        self.redis.delete("resque:queue:Detect")
        QueuedDetector.queue = None

        self.request = mock.Mock(
            image_url="/image/test.jpg",
            detection_error=False,
        )

        self.ctx = mock.Mock(
            config=self.config,
            request=self.request,
        )

    @gen_test
    async def test_detector_sends_to_queue(self):
        await self.detector_send_to_queues(self.ctx)

    @gen_test
    async def test_detector_fails_properly(self):
        self.ctx.config.REDIS_QUEUE_SENTINEL_INSTANCES = "localhost:23680"
        await self.detector_fails_properly(self.ctx)

    @gen_test
    async def test_detector_can_detect_twice(self):
        await self.detector_can_detect_twice(self.ctx)
