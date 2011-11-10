#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import abspath, dirname, join, exists
import shutil
import time

from jinja2 import FileSystemLoader, Environment
from tornado.options import parse_config_file

#required for importing configuration
import thumbor.app
import thumbor.handlers


REPETITIONS = 200
IMAGE_NAME = 'fred'

def get_engine(engine_name):
    module_name = 'thumbor.engines.%s' % engine_name
    module = __import__(module_name)
    return reduce(getattr, module_name.split('.')[1:], module).Engine

def main():
    root = abspath(dirname(__file__))
    image = join(root, '%s.jpg' % IMAGE_NAME)

    conf_file = join(root, 'thumbor.conf')
    parse_config_file(conf_file)

    engines = [('PIL', 'pil'), ('ImageMagick', 'imagemagick'), ('GraphicsMagick', 'graphicsmagick'), ('OpenCV', 'opencv')]

    build_dir = join(root, 'build')
    if exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    source = file(image).read()

    originals = []
    resized = []
    qualities = {}
    times = {}

    for key, engine_class_name in engines:
        engine_class = get_engine(engine_class_name)
        engine = engine_class()
        engine.load(source, '.jpg')

        filename = '%s_%s.jpg' % (IMAGE_NAME, key)
        file(join(build_dir, filename), 'w').write(engine.read('.jpg'))
        originals.append((key, filename))

        engine.resize(300, 300)

        filename = '%s_%s_300x300.jpg' % (IMAGE_NAME, key)
        file(join(build_dir, filename), 'w').write(engine.read('.jpg'))
        resized.append((key, '300x300', filename))

        qualities[key] = []
        for quality in range(10):
            if quality == 0:
                continue
            filename = '%s_%s_300x300_%d.jpg' % (IMAGE_NAME, key, quality)
            file(join(build_dir, filename), 'w').write(engine.read('.jpg', quality=quality * 10))
            qualities[key].append(('300x300', quality, filename))

    number_of_engines = len(engines)
    current_engine = 0

    for key, engine_class_name in engines:
        start = time.time()

        print "Started benchmarking of %s" % key
        for i in range(REPETITIONS):
            print "%.2f%%" % (((float(current_engine) * REPETITIONS + i) / (float(number_of_engines) * REPETITIONS)) * 100)
            engine_class = get_engine(engine_class_name)
            engine = engine_class()
            engine.load(source, '.jpg')
            engine.crop(100, 100, 200, 200)
            engine.resize(50, 50)
            result = engine.read('.jpg')

        times[key] = "%.6f" % (time.time() - start)

        current_engine += 1

    loader = FileSystemLoader(root)
    env = Environment(loader=loader)
    template = env.get_template('template.html')
    file(join(build_dir, 'results.html'), 'w').write(template.render(no_resized=originals, resized=resized, qualities=qualities, times=times, image_name=IMAGE_NAME))

if __name__ == '__main__':
    main()
