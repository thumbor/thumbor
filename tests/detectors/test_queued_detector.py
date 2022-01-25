#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from json import loads
from unittest import mock

from preggy import expect
from redis import Redis
from tornado.testing import gen_test

from tests.base import DetectorTestCase
from thumbor.config import Config
from thumbor.detectors.queued_detector import QueuedDetector

TEST_REDIS_HOST = "0.0.0.0"
TEST_REDIS_PORT = 6668
TEST_REDIS_PASSWORD = "hey_you"


class QueuedDetectorTestCase(DetectorTestCase):
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

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        data = await detector.detect()
        expect(data).to_be_empty()
        expect(ctx.request.detection_error).to_be_false()

        result = self.redis.get("resque:unique:queue:Detect:/image/test.jpg")
        expect(result).to_equal("1")

        expected_payload = {
            "queue": "Detect",
            "args": ["all", "/image/test.jpg", "/image/test.jpg"],
            "class": "remotecv.pyres_tasks.DetectTask",
            "key": "/image/test.jpg",
        }

        result = self.redis.lpop("resque:queue:Detect")
        expect(loads(result.decode("utf-8"))).to_be_like(expected_payload)

    @gen_test
    async def test_detector_fails_properly(self):
        ctx = mock.Mock(
            config=mock.Mock(
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

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        data = await detector.detect()
        expect(data).to_be_empty()
        expect(ctx.request.detection_error).to_be_true()
        expect(detector.queue).to_be_null()

    @gen_test
    async def test_detector_can_detect_twice(self):
        ctx = mock.Mock(
            config=mock.Mock(
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

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        data = await detector.detect()
        expect(data).to_be_empty()
        expect(ctx.request.detection_error).to_be_false()
        expect(detector.queue).not_to_be_null()

        data = detector.detect()
        expect(detector.queue).not_to_be_null()
