#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

import cv

from thumbor.filters import BaseFilter, filter_method

CASCADE_FILE_PATH = abspath(join(dirname(__file__), 'haarcascade_eye.xml'))

MIN_SIZE = (20, 20)
HAAR_SCALE = 1.2
MIN_NEIGHBORS = 3
HAAR_FLAGS = 0
RED_THRESHOLD = 2.0


class Filter(BaseFilter):

    def get_pixels(self, image, w, h, mode):
        pixels = []

        for row in range(h):
            for col in range(w):
                pixel = cv.Get2D(image, row, col)

                pixels.append({
                    'x': col,
                    'y': row,
                    'r': pixel[mode.index('r')],
                    'g': pixel[mode.index('g')],
                    'b': pixel[mode.index('b')]
                })

        return pixels

    def filter_eyes(self, eyes):
        intersected_eyes = []

        for eye in eyes:
            # if eye in intersected_eyes: continue
            (x, y, w, h), other = eye
            for eye2 in eyes:
                (x2, y2, w2, h2), other2 = eye2
                if x == x2 and w == w2 and y == y2 and h == h2:
                    continue
                # if eye2 in intersected_eyes: continue

                if (y2 >= y and y2 + h2 <= y + h) or (y2 + h2 >= y and y2 <= y + h):
                    intersected_eyes.append(eye)
                    # intersected_eyes.append(eye2)

        return intersected_eyes

    @filter_method()
    def red_eye(self):
        self.load_cascade_file()
        faces = [face for face in self.context.request.focal_points if face.origin == 'Face Detection']
        if faces:
            engine = self.context.modules.engine
            mode, data = engine.image_data_as_rgb()
            mode = mode.lower()
            sz = engine.size
            image = cv.CreateImageHeader(sz, cv.IPL_DEPTH_8U, 3)
            cv.SetData(image, data)

            for face in faces:
                face_x = int(face.x - face.width / 2)
                face_y = int(face.y - face.height / 2)

                face_roi = (
                    int(face_x),
                    int(face_y),
                    int(face.width),
                    int(face.height)
                )

                cv.SetImageROI(image, face_roi)

                eyes = cv.HaarDetectObjects(
                    image,
                    self.cascade,
                    cv.CreateMemStorage(0),
                    HAAR_SCALE,
                    MIN_NEIGHBORS,
                    HAAR_FLAGS,
                    MIN_SIZE)

                for (x, y, w, h), other in self.filter_eyes(eyes):
                    # Set the image Region of interest to be the eye area [this reduces processing time]
                    cv.SetImageROI(image, (face_x + x, face_y + y, w, h))

                    if self.context.request.debug:
                        cv.Rectangle(
                            image,
                            (0, 0),
                            (w, h),
                            cv.RGB(255, 255, 255),
                            2,
                            8,
                            0
                        )

                    for pixel in self.get_pixels(image, w, h, mode):
                        green_blue_avg = (pixel['g'] + pixel['b']) / 2

                        if not green_blue_avg:
                            red_intensity = RED_THRESHOLD
                        else:
                            # Calculate the intensity compared to blue and green average
                            red_intensity = pixel['r'] / green_blue_avg

                        # If the red intensity is greater than 2.0, lower the value
                        if red_intensity >= RED_THRESHOLD:
                            new_red_value = (pixel['g'] + pixel['b']) / 2
                            # Insert the new red value for the pixel to the image
                            cv.Set2D(
                                image,
                                pixel['y'],
                                pixel['x'],
                                cv.RGB(new_red_value, pixel['g'], pixel['b'])
                            )

                    # Reset the image region of interest back to full image
                    cv.ResetImageROI(image)

            self.context.modules.engine.set_image_data(image.tostring())

    def load_cascade_file(self):
        if not hasattr(self.__class__, 'cascade'):
            setattr(self.__class__, 'cascade', cv.Load(CASCADE_FILE_PATH))
