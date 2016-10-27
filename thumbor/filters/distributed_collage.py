#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: vertical distribution
# TODO: separator line between images
# TODO: custom alignment

import logging
import math
from os.path import abspath, dirname, isabs, join, splitext

import cv2
import numpy as np
import tornado.gen
from thumbor.filters import BaseFilter, filter_method
from thumbor.loaders import LoaderResult
from thumbor.point import FocalPoint


def calc_new_size_by_height(width, height, bound):
    new_width = width * (bound * 100 / float(height)) / float(100)
    return (new_width, bound)


class StandaloneFaceDetector:
    cascade = None
    HAIR_OFFSET = 0.12

    @classmethod
    def get_cascade_path(cls, cascade_file_path):
        if isabs(cascade_file_path):
            return cascade_file_path
        else:
            return join(
                abspath(join(dirname(__file__), '../detectors/face_detector')),
                cascade_file_path)

    @classmethod
    def get_cascade(cls, context):
        if cls.cascade is None:
            cascade_path = cls.get_cascade_path(context.config.FACE_DETECTOR_CASCADE_FILE)
            cls.cascade = cv2.CascadeClassifier(cascade_path)
        return cls.cascade

    @classmethod
    def get_min_size_for(cls, size):
        ratio = int(min(size) / 15)
        ratio = max(20, ratio)
        return (ratio, ratio)

    @classmethod
    def get_features(cls, context, engine):
        img = np.array(engine.convert_to_grayscale(update_image=False, with_alpha=False))
        faces = cls.get_cascade(context).detectMultiScale(
            img, 1.2, 4, minSize=cls.get_min_size_for(engine.size))
        faces_scaled = []
        for (x, y, w, h) in faces:
            faces_scaled.append(((x.item(), y.item(), w.item(), h.item()), 0))
        return faces_scaled

    @classmethod
    def get_center_of_mass(cls, focal_points):
        total_weight = 0.0
        total_x = 0.0
        total_y = 0.0

        for focal_point in focal_points:
            total_weight += focal_point.weight

            total_x += focal_point.x * focal_point.weight
            total_y += focal_point.y * focal_point.weight

        x = total_x / total_weight
        y = total_y / total_weight

        return x, y

    @classmethod
    def auto_crop(cls, engine, focal_points, target_width=1, target_height=1):
        source_width, source_height = engine.size

        source_ratio = round(float(source_width) / source_height, 2)
        target_ratio = round(float(target_width) / target_height, 2)

        if source_ratio == target_ratio:
            return

        focal_x, focal_y = cls.get_center_of_mass(focal_points)
        if target_width / source_width > target_height / source_height:
            crop_width = source_width
            crop_height = int(round(source_width * target_height / target_width, 0))
        else:
            crop_width = int(round(math.ceil(target_width * source_height / target_height), 0))
            crop_height = source_height

        crop_left = int(round(min(max(focal_x - (crop_width / 2), 0.0), source_width - crop_width)))
        crop_right = min(crop_left + crop_width, source_width)

        crop_top = int(round(min(max(focal_y - (crop_height / 2), 0.0), source_height - crop_height)))
        crop_bottom = min(crop_top + crop_height, source_height)

        engine.crop(crop_left, crop_top, crop_right, crop_bottom)

    @classmethod
    def add_hair_offset(cls, top, height):
        top = max(0, top - height * cls.HAIR_OFFSET)
        return top

    @classmethod
    def features_to_focal_points(cls, features):
        focal_points = []
        for (left, top, width, height), neighbors in features:
            top = cls.add_hair_offset(top, height)
            focal_points.append(
                FocalPoint.from_square(left, top, width, height, origin="Face Detection"))
        return focal_points


class Picture:
    def __init__(self, url, thumbor_filter):
        self.url = url
        self.thumbor_filter = thumbor_filter
        self.extension = splitext(url)[-1].lower()
        self.engine = None
        self.fetched = False
        self.failed = False

    def fill_buffer(self, buffer):
        if (self.engine is None):
            self.engine = self.thumbor_filter.create_engine()
        self.buffer = buffer
        self.fetched = True

    def request(self):
        try:
            self.thumbor_filter.context.modules.loader.load(
                self.thumbor_filter.context, self.url, self.on_fetch_done)
        except Exception, err:
            self.error(err)

    def save_on_disc(self):
        if self.fetched:
            try:
                self.engine.load(self.buffer, self.extension)
            except Exception, err:
                self.error(err)

            try:
                self.thumbor_filter.storage.put(self.url, self.engine.read())
                self.thumbor_filter.storage.put_crypto(self.url)
            except Exception, err:
                self.error(err)
        else:
            self.error("Can't save unfetched image")

    def on_fetch_done(self, result):
        # TODO if result.successful is False how can the error be handled?
        self.fill_buffer(result.buffer if isinstance(result, LoaderResult) else result)
        self.save_on_disc()
        self.thumbor_filter.on_image_fetch()

    def process(self, canvas_width, canvas_height, size):
        try:
            self.engine.load(self.buffer, self.extension)
            width, height = self.engine.size
            if width > height:
                self.engine.resize(*calc_new_size_by_height(
                    width, height, canvas_height))
            focal_points = StandaloneFaceDetector.features_to_focal_points(
                StandaloneFaceDetector.get_features(self.thumbor_filter.context, self.engine))
            self.engine.focus(focal_points)
            StandaloneFaceDetector.auto_crop(self.engine, focal_points, size, canvas_height)
        except Exception, err:
            logging.error(err)

    def error(self, msg):
        logging.error(msg)
        self.failed = True


class Filter(BaseFilter):
    regex = r'(?:distributed_collage\((?P<orientation>horizontal),(?P<alignment>smart),(?P<urls>[^\)]+)\))'
    MAX_IMAGES = 4

    @filter_method(r'horizontal', r'smart', r'[^\)]+', async=True)
    @tornado.gen.coroutine
    def distributed_collage(self, callback, orientation, alignment, urls):
        logging.debug('distributed_collage invoked')
        self.storage = self.context.modules.storage

        self.callback = callback
        self.orientation = orientation
        self.alignment = alignment
        self.urls = urls.split('|')
        self.images = {}

        total = len(self.urls)
        if total > self.MAX_IMAGES:
            logging.error('Too many images to join')
            callback()
        elif total == 0:
            logging.error('No images to join')
            callback()
        else:
            self.urls = self.urls[:self.MAX_IMAGES]
            for url in self.urls:
                self.images[url] = Picture(url, self)

            # second loop needed to ensure that all images are in self.images
            # otherwise, self.on_image_fetch can call the self.assembly()
            # without that all images had being loaded
            for url in self.urls:
                buffer = yield tornado.gen.maybe_future(self.storage.get(url))
                pic = self.images[url]
                if buffer is not None:
                    pic.fill_buffer(buffer)
                    self.on_image_fetch()
                else:
                    pic.request()

    def is_all_fetched(self):
        return all([self.images[url].fetched for url in self.images])

    def is_any_failed(self):
        return any([self.images[url].failed for url in self.images])

    def create_engine(self):
        try:
            return self.context.modules.engine.__class__(self.context)
        except Exception, err:
            logging.error(err)

    def on_image_fetch(self):
        if (self.is_any_failed()):
            logging.error('some images failed')
            self.callback()
        elif self.is_all_fetched():
            self.assembly()

    def divide_size(self, size, parts):
        """
        Solves the problem with division where the result isn't integer.
        For example, when dividing a 100px image in 3 parts, the collage
        division should be like 33px + 33px + 34px = 100px. In this case,
        slice_size is 33px and major_slice_size is 34px.
        """
        slice_size = size / float(parts)
        major_slice_size = math.ceil(slice_size)
        slice_size = math.floor(slice_size)
        return int(slice_size), int(major_slice_size)

    def assembly(self):
        logging.debug('assembly started')
        canvas = self.create_engine()
        canvas_width, canvas_height = self.engine.size
        canvas.image = canvas.gen_image((canvas_width, canvas_height), '#fff')

        i = 0
        total = len(self.images)
        slice_size, major_slice_size = self.divide_size(canvas_width, total)
        for url in self.urls:
            image = self.images[url]
            x, y = i * slice_size, 0
            if i + 1 == total:
                slice_size = major_slice_size
            try:
                image.process(canvas_width, canvas_height, slice_size)
                canvas.paste(image.engine, (x, y), merge=True)
            except Exception, err:
                logging.error(err)
            i += 1

        self.engine.image = canvas.image
        logging.debug('assembled')
        self.callback()
