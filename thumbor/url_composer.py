#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import sys
import optparse

from tornado.options import options, parse_config_file

from thumbor import __version__
from thumbor.crypto import Crypto
from thumbor.app import ThumborServiceApp

def main(arguments=[]):
    '''Converts a given url with the specified arguments.'''

    parser = optparse.OptionParser(usage='thumbor-url [options] imageurl or type thumbor-url -h (--help) for help', description=__doc__, version=__version__)

    parser.add_option('-k', '--key', dest='key', default=None, help = 'The security key to encrypt the url with [default: %default].' )
    parser.add_option('-w', '--width', dest='width', type='int', default=0, help = 'The target width for the image [default: %default].' )
    parser.add_option('-e', '--height', dest='height', type='int', default=0, help = 'The target height for the image [default: %default].' )
    parser.add_option('-n', '--fitin', dest='fitin', action='store_true', default=False, help = 'Indicates that fit-in resizing should be performed.' )
    parser.add_option('-s', '--smart', action='store_true', dest='smart', default=False, help = 'Indicates that smart cropping should be used.' )
    parser.add_option('-f', '--horizontal-flip', action='store_true', dest='horizontal_flip', default=False, help = 'Indicates that the image should be horizontally flipped.' )
    parser.add_option('-v', '--vertical-flip', action='store_true', dest='vertical_flip', default=False, help = 'Indicates that the image should be vertically flipped.')
    parser.add_option('-a', '--halign', dest='halign', default='center', help = 'The horizontal alignment to use for cropping [default: %default].' )
    parser.add_option('-i', '--valign', dest='valign', default='middle', help = 'The vertical alignment to use for cropping [default: %default].' )

    parser.add_option('-c', '--crop', dest='crop', default=None, help = 'The coordinates of the points to manual cropping in the format leftxtop:rightxbottom (100x200:400x500) [default: %default].' )

    (parsed_options, arguments) = parser.parse_args(arguments)

    if not arguments:
        print 'Error: The image argument is mandatory. For more information type thumbor-url -h'
        return

    image_url = arguments[0]
    if image_url.startswith('/'):
        image_url = image_url[1:]

    conf_file = ThumborServiceApp.get_conf_file('')
    if conf_file:
        print
        print "USING CONFIGURATION FILE AT %s" % conf_file
        print
        parse_config_file(conf_file)

    if not parsed_options.key and not conf_file:
        print 'Error: The -k or --key argument is mandatory. For more information type thumbor-url -h'
        return

    security_key = options.SECURITY_KEY if not parsed_options.key else parsed_options.key

    crypt = Crypto(security_key)

    crop_left = crop_top = crop_right = crop_bottom = 0
    if parsed_options.crop:
        crops = parsed_options.crop.split(':')
        crop_left, crop_top = crops[0].split('x')
        crop_right, crop_bottom = crops[1].split('x')

    opt = crypt.encrypt(parsed_options.width,
                        parsed_options.height,
                        parsed_options.smart,
                        parsed_options.fitin,
                        parsed_options.horizontal_flip,
                        parsed_options.vertical_flip,
                        parsed_options.halign,
                        parsed_options.valign,
                        crop_left,
                        crop_top,
                        crop_right,
                        crop_bottom,
                        image_url)
    url = '/%s/%s' % (opt, image_url)

    print 'Encrypted URL: "%s" (without quotes)' % url

if __name__ == '__main__':
    main(sys.argv)
