#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from os.path import abspath, dirname, join

import cv2
import numpy as np

from thumbor.filters import BaseFilter, filter_method

CASCADE_FILE_PATH = abspath(join(dirname(__file__), 'haarcascade_eye.xml'))

MIN_SIZE = (20, 20)
HAAR_SCALE = 1.2
MIN_NEIGHBORS = 3
RED_THRESHOLD = 2.0


class Filter(BaseFilter):
    @filter_method()
    def red_eye(self):
        faces = [face for face in self.context.request.focal_points if face.origin == 'Face Detection']
        if not faces:
            return

        mode, data = self.engine.image_data_as_rgb()
        mode = mode.lower()
        size = self.engine.size

        image = np.ndarray(shape=(size[1], size[0], 4 if mode == 'rgba' else 3), dtype='|u1', buffer=data)
        image.setflags(write=1)

        for face in faces:
            face_x = int(face.x - face.width / 2)
            face_y = int(face.y - face.height / 2)

            face_image = image[face_y:face_y + face.height, face_x:face_x + face.width]

            eyeRects = self.cascade.detectMultiScale(
                face_image,
                scaleFactor=HAAR_SCALE,
                minNeighbors=MIN_NEIGHBORS,
                minSize=MIN_SIZE)

            for x, y, w, h in eyeRects:
                # Crop the eye region
                eyeImage = face_image[y:y + h, x:x + w]

                # split the images into 3 channels
                r, g, b = cv2.split(eyeImage)

                # Add blue and green channels
                bg = cv2.add(b, g)
                mean = bg / 2
                # threshold the mask based on red color and combination of blue and green color
                mask = ((r > RED_THRESHOLD * mean) & (r > 60)).astype(np.uint8) * 255
                # Some extra region may also get detected , we find the largest region
                # find all contours
                contours_return = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_NONE)  # It return contours and Hierarchy

                if len(contours_return) == 2:
                    contours, _ = contours_return
                else:
                    _, contours, _ = contours_return

                # find contour with max area
                maxArea = 0
                maxCont = None
                for cont in contours:
                    area = cv2.contourArea(cont)
                    if area > maxArea:
                        maxArea = area
                        maxCont = cont

                if maxCont is None:
                    continue

                mask = mask * 0  # Reset the mask image to complete black image
                # draw the biggest contour on mask
                cv2.drawContours(mask, [maxCont], 0, (255), -1)
                # Close the holes to make a smooth region
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_DILATE, (5, 5)))
                mask = cv2.dilate(mask, (3, 3), iterations=3)

                # The information of only red color is lost,
                # So we fill the mean of blue and green color in all three channels(BGR) to maintain the texture
                # Fill this black mean value to masked image
                mean = cv2.bitwise_and(mean, mask)  # mask the mean image
                mean = cv2.cvtColor(mean, cv2.COLOR_GRAY2RGB)  # convert mean to 3 channel
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)  # convert mask to 3 channel
                eye = cv2.bitwise_and(~mask, eyeImage) + mean  # Copy the mean color to masked region to color image
                face_image[y:y + h, x:x + w] = eye

        self.engine.set_image_data(image.tobytes())

    @property
    def cascade(self):
        if not hasattr(self, '_cascade'):
            setattr(self, '_cascade', cv2.CascadeClassifier(CASCADE_FILE_PATH))

        return getattr(self, '_cascade')
