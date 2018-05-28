#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from unittest import TestCase
import mock
from json import loads

from redis import Redis
from preggy import expect

from thumbor.detectors.queued_detector import QueuedDetector


class QueuedDetectorTestCase(TestCase):
    def setUp(self, *args, **kw):
        super(QueuedDetectorTestCase, self).setUp(*args, **kw)
        self.redis = Redis(
            host='0.0.0.0',
            port=6668,
            db=0,
            password='hey_you',
        )

        self.redis.delete('resque:unique:queue:Detect:/image/test.jpg')
        self.redis.delete('resque:queue:Detect')
        QueuedDetector.queue = None

    def test_detector_sends_to_queue(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_SERVER_HOST='0.0.0.0',
                REDIS_QUEUE_SERVER_PORT=6668,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD='hey_you',
            ),
            request=mock.Mock(
                image_url='/image/test.jpg',
                detection_error=False,
            ),
        )

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        def validate(data):
            expect(data).to_be_empty()

        detector.detect(validate)
        expect(ctx.request.detection_error).to_be_false()

        result = self.redis.get('resque:unique:queue:Detect:/image/test.jpg')
        expect(result).to_equal('1')

        expected_payload = {
            "queue": "Detect",
            "args": ["all", "/image/test.jpg", "/image/test.jpg"],
            "class": "remotecv.pyres_tasks.DetectTask",
            "key": "/image/test.jpg"
        }

        result = self.redis.lpop('resque:queue:Detect')
        expect(loads(result)).to_be_like(expected_payload)

    def test_detector_fails_properly(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_SERVER_HOST='0.0.0.0',
                REDIS_QUEUE_SERVER_PORT=6669,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD='hey_you',
            ),
            request=mock.Mock(
                image_url='/image/test.jpg',
                detection_error=False,
            ),
        )

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        def validate(data):
            expect(data).to_be_empty()

        detector.detect(validate)
        expect(ctx.request.detection_error).to_be_true()
        expect(detector.queue).to_be_null()

    def test_detector_can_detect_twice(self):
        ctx = mock.Mock(
            config=mock.Mock(
                REDIS_QUEUE_SERVER_HOST='0.0.0.0',
                REDIS_QUEUE_SERVER_PORT=6668,
                REDIS_QUEUE_SERVER_DB=0,
                REDIS_QUEUE_SERVER_PASSWORD='hey_you',
            ),
            request=mock.Mock(
                image_url='/image/test.jpg',
                detection_error=False,
            ),
        )

        detector = QueuedDetector(ctx, 1, [])
        expect(detector).not_to_be_null()

        def validate(data):
            expect(data).to_be_empty()

        detector.detect(validate)
        expect(ctx.request.detection_error).to_be_false()
        expect(detector.queue).not_to_be_null()

        detector.detect(validate)
        expect(detector.queue).not_to_be_null()
