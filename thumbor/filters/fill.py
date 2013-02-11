#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):

    def get_median_color(self):
        # importing opencv here
        # so thumbor keeps not depending on it
        # for the basic features
        import cv

        sz = self.engine.size
        mode, converted_image = self.engine.convert_to_rgb()

        image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, converted_image)

        # Prepare the data for K-means. Represent each pixel in the image as a 3D
        # vector (each dimension corresponds to one of B,G,R color channel value).
        # Create a column of such vectors -- it will be width * height tall, 1 wide
        # and have a total of 3 channels.
        col = cv.Reshape(image, 3, image.width * image.height)
        samples = cv.CreateMat(col.height, 1, cv.CV_32FC3)
        cv.Scale(col, samples)
        labels = cv.CreateMat(col.height, 1, cv.CV_32SC1)

        # Run 10 iterations of the K-means algorithm.
        termination_criteria = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 10, 1.0)
        # one cluster of pixels
        cv.KMeans2(samples, 1, labels, termination_criteria)

        sum_r = sum_g = sum_b = 0
        n_pixels = col.rows
        for i in xrange(n_pixels):
            r, g, b, _ = cv.Get1D(samples, i)
            sum_r += r
            sum_g += g
            sum_b += b

        # Determine the center of the cluster. The old OpenCV interface (C-style)
        # doesn't seem to provide an easy way to get these directly, so we have to
        # calculate them ourselves.
        r = int(sum_r / n_pixels)
        g = int(sum_g / n_pixels)
        b = int(sum_b / n_pixels)

        return '{:02x}{:02x}{:02x}'.format(r, g, b)

    @filter_method(r'[\w]+')
    def fill(self, value):

        self.fill_engine = self.engine.__class__(self.context)
        bx = self.context.request.width if self.context.request.width != 0 else self.engine.image.size[0]
        by = self.context.request.height if self.context.request.height != 0 else self.engine.image.size[1]

        # if the value is 'auto'
        # we will use kmeans (from opencv) to define
        # the most predominant color on the image
        # and set it is the filling color
        # more info:
        # http://stackoverflow.com/questions/3923906/kmeans-in-opencv-python-interface
        # http://docs.opencv.org/modules/core/doc/clustering.html
        # credits to misha http://stackoverflow.com/users/356020/misha
        if value == 'auto':
            value = self.get_median_color()

        try:
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), value)
        except (ValueError, RuntimeError):
            self.fill_engine.image = self.fill_engine.gen_image((bx, by), '#%s' % value)

        ix, iy = self.engine.size

        px = (bx - ix) / 2  # top left
        py = (by - iy) / 2

        self.fill_engine.paste(self.engine, (px, py), merge=False)
        self.engine.image = self.fill_engine.image
