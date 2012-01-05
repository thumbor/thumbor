from tornado import ioloop
from tornado.options import options

import datetime

import bson
import zmq
from zmq.eventloop import zmqstream

from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint

class RemoteDetector(BaseDetector):
    zmq_ctx = None

    def get_context(self):
        if RemoteDetector.zmq_ctx is None:
            RemoteDetector.zmq_ctx = zmq.Context()

        return RemoteDetector.zmq_ctx

    def detect(self, context, callback):
        self.context = context
        self.callback = callback
        self.ioloop = ioloop.IOLoop.instance()
        self.get_features()

    def on_result(self, data):
        self.ioloop.remove_timeout(self.timeout_handle)
        self.stream.close()
        features = bson.loads(data[0])['points']
        if features:
            for (left, top, width, height) in features:
                self.context['focal_points'].append(FocalPoint.from_square(left, top, width, height, origin="Face Detection"))
            self.callback()
        else:
            self.next(self.context, self.callback)

    def on_timeout(self):
        logger.warning('timeout for remote detector %s' % self.__class__.__module__)
        self.stream.close()
        self.context['detector_error'] = True
        self.callback()

    def get_features(self):
        engine = self.context['engine']
        image = engine.get_image_data()

        ctx = self.get_context()

        socket = ctx.socket(zmq.REQ)
        socket.connect('tcp://%s:%s' % (options.REMOTECV_HOST, options.REMOTECV_PORT))
        socket.setsockopt(zmq.LINGER, 0)

        self.timeout_handle = self.ioloop.add_timeout(datetime.timedelta(seconds=options.REMOTECV_TIMEOUT), self.on_timeout)
        self.stream = zmqstream.ZMQStream(socket, self.ioloop)
        self.stream.on_recv(self.on_result)

        msg = { 
            'type': self.detection_type,
            'size': engine.size,
            'mode': engine.get_image_mode(),
            'path': self.context['image_url']
        }

        if options.REMOTECV_SEND_IMAGE:
            msg['image'] = image
            
        self.stream.send(bson.dumps(msg))

