#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import sys
import optparse
from urllib import quote

from thumbor import __version__
from libthumbor import CryptoURL
from thumbor.config import Config


def get_parser():
    parser = optparse.OptionParser(
        usage='thumbor-url [options] imageurl or type thumbor-url -h (--help) for help',
        description=__doc__,
        version=__version__
    )

    parser.add_option(
        '-l', '--key_file', dest='key_file', default=None, help='The file to read the security key from [default: %default].'
    )
    parser.add_option(
        '-k', '--key', dest='key', default=None, help='The security key to encrypt the url with [default: %default].'
    )
    parser.add_option(
        '-w', '--width', dest='width', type='int', default=0, help='The target width for the image [default: %default].'
    )
    parser.add_option(
        '-e', '--height', dest='height', type='int', default=0, help='The target height for the image [default: %default].'
    )
    parser.add_option(
        '-n', '--fitin', dest='fitin', action='store_true', default=False,
        help='Indicates that fit-in resizing should be performed.'
    )
    parser.add_option(
        '-m', '--meta', dest='meta', action='store_true', default=False,
        help='Indicates that meta information should be retrieved.'
    )
    parser.add_option(
        '', '--adaptive', action='store_true', dest='adaptive', default=False,
        help='Indicates that adaptive fit-in cropping should be used.'
    )
    parser.add_option(
        '', '--full', action='store_true', dest='full', default=False, help='Indicates that fit-full cropping should be used.'
    )
    parser.add_option(
        '-s', '--smart', action='store_true', dest='smart', default=False, help='Indicates that smart cropping should be used.'
    )
    parser.add_option(
        '-t', '--trim', action='store_true', default=False, help='Indicate that surrounding whitespace should be trimmed.'
    )
    parser.add_option(
        '-f', '--horizontal-flip', action='store_true', dest='horizontal_flip', default=False,
        help='Indicates that the image should be horizontally flipped.'
    )
    parser.add_option(
        '-v', '--vertical-flip', action='store_true', dest='vertical_flip', default=False,
        help='Indicates that the image should be vertically flipped.'
    )
    parser.add_option(
        '-a', '--halign', dest='halign', default='center',
        help='The horizontal alignment to use for cropping [default: %default].'
    )
    parser.add_option(
        '-i', '--valign', dest='valign', default='middle',
        help='The vertical alignment to use for cropping [default: %default].'
    )
    parser.add_option(
        '', '--filters', dest='filters', action='append',
        help='Filters to be applied to the image, e.g. brightness(10).'
    )
    parser.add_option(
        '-o', '--old-format', dest='old', action='store_true', default=False,
        help='Indicates that thumbor should generate old-format urls [default: %default].'
    )

    parser.add_option(
        '-c', '--crop', dest='crop', default=None,
        help='The coordinates of the points to manual cropping in the format leftxtop:rightxbottom '
        '(100x200:400x500) [default: %default].'
    )

    return parser


def get_options(arguments):
    if arguments is None:
        arguments = sys.argv[1:]

    parser = get_parser()

    (parsed_options, arguments) = parser.parse_args(arguments)

    if not arguments:
        sys.stdout.write('Error: The image argument is mandatory. For more information type thumbor-url -h\n')
        return

    return parsed_options, arguments


def get_thumbor_params(image_url, params, config):
    if params.key_file:
        f = open(params.key_file)
        security_key = f.read().strip()
        f.close()
    else:
        security_key = config.SECURITY_KEY if not params.key else params.key

    crop_left = crop_top = crop_right = crop_bottom = 0
    if params.crop:
        crops = params.crop.split(':')
        crop_left, crop_top = crops[0].split('x')
        crop_right, crop_bottom = crops[1].split('x')

    options = {
        'old': params.old,
        'width': params.width,
        'height': params.height,
        'smart': params.smart,
        'meta': params.meta,
        'horizontal_flip': params.horizontal_flip,
        'vertical_flip': params.vertical_flip,
        'halign': params.halign,
        'valign': params.valign,
        'trim': params.trim,
        'crop_left': crop_left,
        'crop_top': crop_top,
        'crop_right': crop_right,
        'crop_bottom': crop_bottom,
        'filters': params.filters,
        'image_url': image_url,
        'fit_in': False,
        'full_fit_in': False,
        'adaptive_fit_in': False,
        'adaptive_full_fit_in': False,
    }

    if params.fitin and params.full and params.adaptive:
        options['adaptive_full_fit_in'] = True
    elif params.fitin and params.full:
        options['full_fit_in'] = True
    elif params.fitin and params.adaptive:
        options['adaptive_fit_in'] = True
    elif params.fitin:
        options['fit_in'] = True

    return security_key, options


def main(arguments=None):
    '''Converts a given url with the specified arguments.'''

    parsed_options, arguments = get_options(arguments)

    image_url = arguments[0]
    image_url = quote(image_url)

    try:
        config = Config.load(None)
    except:
        config = None

    if not parsed_options.key and not config:
        sys.stdout.write('Error: The -k or --key argument is mandatory. For more information type thumbor-url -h\n')
        return

    security_key, thumbor_params = get_thumbor_params(image_url, parsed_options, config)

    crypto = CryptoURL(key=security_key)
    url = crypto.generate(**thumbor_params)
    sys.stdout.write('URL:\n')
    sys.stdout.write('%s\n' % url)

    return url


if __name__ == '__main__':
    main(sys.argv[1:])
