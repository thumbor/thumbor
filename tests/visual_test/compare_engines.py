#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import abspath, dirname, join, exists
import shutil

from jinja2 import FileSystemLoader, Environment
from tornado.options import parse_config_file

import thumbor.app
import thumbor.handlers

def get_engine(engine_name):
    module_name = 'thumbor.engines.%s' % engine_name
    module = __import__(module_name)
    return reduce(getattr, module_name.split('.')[1:], module).Engine

def main():
    root = abspath(dirname(__file__))
    image = join(root, 'flower.jpg')

    conf_file = join(root, 'thumbor.conf')
    parse_config_file(conf_file)

    engines = [('PIL', 'pil'), ('ImageMagick', 'imagemagick'), ('GraphicsMagick', 'graphicsmagick')]

    build_dir = join(root, 'build')
    if exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    source = file(image).read()

    originals = []
    resized = []
    qualities = {}

    for key, engine_class_name in engines:
        engine_class = get_engine(engine_class_name)
        engine = engine_class()
        engine.load(source)

        filename = 'flower_%s.jpg' % key
        file(join(build_dir, filename), 'w').write(engine.read('.jpg'))
        originals.append((key, filename))

        engine.resize(300, 300)

        filename = 'flower_%s_300x300.jpg' % key
        file(join(build_dir, filename), 'w').write(engine.read('.jpg'))
        resized.append((key, '300x300', filename))

        qualities[key] = []
        for quality in range(10):
            if quality == 0:
                continue
            filename = 'flower_%s_300x300_%d.jpg' % (key, quality)
            file(join(build_dir, filename), 'w').write(engine.read('.jpg', quality=quality * 10))
            qualities[key].append(('300x300', quality, filename))

    loader = FileSystemLoader(root)
    env = Environment(loader=loader)
    template = env.get_template('template.html')
    file(join(build_dir, 'results.html'), 'w').write(template.render(no_resized=originals, resized=resized, qualities=qualities))

if __name__ == '__main__':
    main()
