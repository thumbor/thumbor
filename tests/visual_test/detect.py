#!/usr/bin/env python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import glob
import os
import tempfile
import sys
from os.path import dirname, abspath, join, basename, splitext, exists

import cv
from tornado.options import define

define('MAGICKWAND_PATH', [])

__dirname = abspath(dirname(__file__))
sys.path.insert(0, abspath(join(__dirname, '..', '..')))

from thumbor.vendor.pythonmagickwand.image import Image


cascade_files = (
    join('face_detector', 'haarcascade_frontalface_alt.xml'),
    join('profile_detector', 'haarcascade_profileface.xml'),
    join('glasses_detector', 'haarcascade_eye_tree_eyeglasses.xml')
)

cascade_files = [abspath(join(__dirname, '..', '..', 'thumbor', 'detectors', cascade_file)) for cascade_file in cascade_files]

images_path = glob.glob(abspath(join(__dirname, '..', 'fixtures', 'img', '*.*')))

for cascade_file in cascade_files:
    loaded_cascade_file = cv.Load(cascade_file)

    for image_path in images_path:

        with tempfile.NamedTemporaryFile() as temp_file:
            file_name = temp_file.name

            # imagick
            img = Image(image_path)
            img.format = 'JPEG'
            img.save(file_name)

            # pil
            # PILImage.open(image_path).convert('RGB').save(file_name, 'JPEG')

            grayscale = cv.LoadImageM(file_name, cv.CV_LOAD_IMAGE_GRAYSCALE)

            faces = cv.HaarDetectObjects(
                grayscale, loaded_cascade_file,
                cv.CreateMemStorage(), 1.1, 3, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))

            if faces:
                for (left, top, width, height), neighbors in faces:
                    cv.Rectangle(
                        grayscale,
                        (int(left), int(top)),
                        (int(left + width), int(top + height)),
                        255
                    )
                cascade_file_name = splitext(basename(cascade_file))[0]
                destination_folder = join(__dirname, 'img')
                if not exists(destination_folder):
                    os.makedirs(destination_folder)
                cv.SaveImage(join(destination_folder, '%s_%s' % (cascade_file_name, basename(image_path))), grayscale)
                print 'face detected on %s using %s' % (basename(image_path), basename(cascade_file))
