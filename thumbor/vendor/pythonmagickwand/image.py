#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import ctypes
import api
import wand
import color

class Image(object):
    ''' Represents a single image, supported by a MagickWand.'''

    def __init__(self, image=None, type=None):
        self._wand = api.NewMagickWand()

        if type:
            api.MagickSetFilename(self._wand, 'buffer.%s' % type)  # hint image type

        if hasattr(image, 'read'):
            c = image.read()
            self._check_wand_error(api.MagickReadImageBlob(self._wand, c, len(c)))
        elif image:
            self._check_wand_error(api.MagickReadImage(self._wand, image))
        else:
            self._check_wand_error(api.MagickNewImage(self._wand, 100, 100, color.TRANSPARENT._wand))

    def __del__(self):
        if self._wand:
            self._wand = api.DestroyMagickWand(self._wand)

    def __copy__(self):
        c = Image()
        if self._wand:
            c._wand = api.CloneMagickWand(self._wand)
        return c

    def _check_wand_error(self, func):
        wand._check_wand_error(self._wand, func)

    def _get_format(self):
        format = api.MagickGetImageFormat(self._wand)
        if format == '':
            return None
        else:
            return format

    def _set_format(self, value):
        self._check_wand_error(api.MagickSetImageFormat(self._wand, value))

    def _get_units(self):
        units = api.MagickGetImageUnits(self._wand)
        if units == api.UndefinedResolution:
            return None
        else:
            return units

    def _set_units(self, value):
        if value and value is wand.PIXELS_PER_INCH or value is wand.PIXELS_PER_CENTIMETER:
            self._check_wand_error(api.MagickSetImageUnits(self._wand, value))
        elif not value:
            self._check_wand_error(api.MagickSetImageUnits(self._wand, api.UndefinedResolution))
        else:
            raise ValueError('units must be one of None, PIXELS_PER_INCH or PIXELS_PER_CENTIMETER')

    def _get_resolution(self):
        x = y = ctypes.c_double()
        self._check_wand_error(api.MagickGetImageResolution(self._wand, x, y))
        return (x.value, y.value)

    def _set_resolution(self, value):
        self._check_wand_error(api.MagickSetImageResolution(self._wand, value[0], value[1]))

    def _get_size(self):
        width = api.MagickGetImageWidth(self._wand)
        height = api.MagickGetImageHeight(self._wand)
        return (width, height)

    def _set_colorspace(self, colorspace):
        self._check_wand_error(api.MagickSetImageColorspace(self._wand, colorspace))

    def _get_colorspace(self):
        colorspace = api.MagickGetImageColorspace(self._wand)
        if colorspace == api.UndefinedColorspace:
            return None
        else:
            return colorspace

    def _get_background_color(self):
        c = color.TRANSPARENT
        self._check_wand_error(api.MagickGetImageBackgroundColor(self._wand, c._wand))
        return c

    def _set_background_color(self, color):
        self._check_wand_error(api.MagickSetImageBackgroundColor(self._wand, color._wand))

    def _get_border_color(self):
        c = color.TRANSPARENT
        self._check_wand_error(api.MagickGetImageBorderColor(self._wand, c._wand))
        return c

    def _set_border_color(self, color):
        self._check_wand_error(api.MagickSetImageBorderColor(self._wand, color._wand))

    def _get_compression(self):
        compression = api.MagickGetImageCompression(self._wand)
        if compression == wand.NO_COMPRESSION:
            return None
        else:
            return compression

    def _set_compression(self, compression):
        if not compression:
            compression = wand.NO_COMPRESSION
        self._check_wand_error(api.MagickSetImageCompression(self._wand, compression))

    def _get_compression_quality(self):
        return api.MagickGetImageCompressionQuality(self._wand)

    def _set_compression_quality(self, quality):
        self._check_wand_error(api.MagickSetImageCompressionQuality(self._wand, int(round(quality, 0))))

    def tostring(self):
        size = api.size_t()
        return api.MagickGetImageBlob(self._wand, size)
        
    def save(self, file=None):
        ''' Saves the image to a file.  If no file is specified, the file is
            saved with the original filename.'''
        if hasattr(file, 'write'):
            size = api.size_t()
            b = api.MagickGetImageBlob(self._wand, size)
            try:
                file.write(''.join([chr(b[i]) for i in range(0, size.value + 1)]))
            finally:
                api.MagickRelinquishMemory(b)
        else:
            self._check_wand_error(api.MagickWriteImage(self._wand, file))

    def dump(self, type=None):
        ''' Save the image to a buffer, if no type is specified, original type is used.

            returns image'''

        if type:
            api.MagickSetFilename(self._wand, 'buffer.%s' % type)  # hint image type

        result = ''
        size = api.size_t()
        b = api.MagickGetImageBlob(self._wand, size)
        try:
            result = ''.join([chr(b[i]) for i in range(0, size.value + 1)])
        finally:
            api.MagickRelinquishMemory(b)

        return result

    def alpha(self, alpha_on):
        ''' Activates alpha channel/matte for further operations.

            alpha_on - Boolean'''

        api.MagickSetImageAlphaChannel(self._wand, alpha_on)

    def select(self, size):
        ''' Selects image of given size if multiple image are available in container.

            size - A tuple containing the size of the scaled image.

            returns True on success.'''

        width, height = size
        api.MagickResetIterator(self._wand)
        loop = True
        while loop:
            _width = api.MagickGetImageWidth(self._wand)
            _height = api.MagickGetImageHeight(self._wand)
            if _width == width and _height == height:
                return True

            loop = api.MagickNextImage(self._wand)

        api.MagickResetIterator(self._wand)
        return False

    def scale(self, size):
        ''' Scales the size of image to the given dimensions.

            size - A tuple containing the size of the scaled image.'''
        self._check_wand_error(api.MagickScaleImage(self._wand, size[0], size[1]))

    def resize(self, size, filter=None, blur=0):
        ''' Resize the image with the given filter and applying some blur.

            size - A tuple containing the size of the scaled image.
            filter - None, or one of BESSEL_FILTER, BLACKMAN_FILTER,
                     BOX_FILTER, CATROM_FILTER, CUBIC_FILTER, GAUSSIAN_FILTER,
                     HANNING_FILTER, HERMITE_FILTER, LANCZOS_FILTER,
                     MITCHELL_FILTER, POINT_FILTER, QUADRATIC_FILTER,
                     SINC_FILTER, or TRIANGLE_FILTER.
             blur - blur factor where > 1 is blurry, < 1 is sharp.  Default is
                    no blur.'''

        if not filter:
            filter = api.UndefinedFilter

        self._check_wand_error(api.MagickResizeImage(self._wand, size[0], size[1], filter, blur))

    def resample(self, resolution, filter=None, blur=0):
        ''' Resample the image with the given filter and applying some blur.

            resolution - A tuple containing the resolution of the resampled image.
            filter - None, or one of BESSEL_FILTER, BLACKMAN_FILTER,
                     BOX_FILTER, CATROM_FILTER, CUBIC_FILTER, GAUSSIAN_FILTER,
                     HANNING_FILTER, HERMITE_FILTER, LANCZOS_FILTER,
                     MITCHELL_FILTER, POINT_FILTER, QUADRATIC_FILTER,
                     SINC_FILTER, or TRIANGLE_FILTER.
             blur - blur factor where > 1 is blurry, < 1 is sharp.  Default is
                    no blur.'''

        if not filter:
            filter = api.UndefinedFilter

        self._check_wand_error(api.MagickResampleImage(self._wand, resolution[0], resolution[1], filter, blur))

    def sharpen(self, radius, sigma, channel=None):
        ''' Sharpen the image with a Gaussian operator of the given radius and
            standard deviation.  For best results, the radius should be larger
            than sigma.  If radius is 0, a suitable radius is automatically
            selected.  If channel is provided, the sharpen is restricted to
            that particular channel.

            radius - The radius of the Gaussian operator, in pixels, not
                     counting the center pixel.
            sigma - The standard deviation of the Gaussian operator, in pixels.
            channel - None, or one of RED_CHANNEL, CYAN_CHANNEL, GREEN_CHANNEL,
                      MAGENTA_CHANNEL, BLUE_CHANNEL, YELLOW_CHANNEL,
                      ALPHA_CHANNEL, OPACITY_CHANNEL, BLACK_CHANNEL,
                      INDEX_CHANNEL, ALL_CHANNELS.'''

        if channel:
            self._check_wand_error(api.MagickSharpenImageChannel(self._wand, channel, radius, sigma))
        else:
            self._check_wand_error(api.MagickSharpenImage(self._wand, radius, sigma))

    def blur(self, radius, sigma, channel=None):
        ''' Blurs the image with a Gaussian operator of the given radius and
            standard deviation.  For best results, the radius should be larger
            than sigma.  If radius is 0, a suitable radius is automatically
            selected.  If channel is provided, the blur is restricted to
            that particular channel.

            radius - The radius of the Gaussian operator, in pixels, not
                     counting the center pixel.
            sigma - The standard deviation of the Gaussian operator, in pixels.
            channel - None, or one of RED_CHANNEL, CYAN_CHANNEL, GREEN_CHANNEL,
                      MAGENTA_CHANNEL, BLUE_CHANNEL, YELLOW_CHANNEL,
                      ALPHA_CHANNEL, OPACITY_CHANNEL, BLACK_CHANNEL,
                      INDEX_CHANNEL, ALL_CHANNELS.'''

        if channel:
            self._check_wand_error(api.MagickBlurImageChannel(self._wand, channel, radius, sigma))
        else:
            self._check_wand_error(api.MagickBlurImage(self._wand, radius, sigma))

    def motion_blur(self, radius, sigma, angle):
        ''' Simulates motion blur in an image by convolving the image with a
            Gaussian operator of the given radius and standard deviation.  For best
            results, the radius should be larger than sigma.  If radius is 0, a
            suitable radius is automatically selected.

            radius - The radius of the Gaussian operator, in pixels, not
                     counting the center pixel.
            sigma - The standard deviation of the Gaussian operator, in pixels.
            angle - Apply the effect along this angle.'''
        self._check_wand_error(api.MagickMotionBlurImage(self._wand, radius, sigma, angle))

    def despeckle(self):
        ''' Reduces the speckle noise in the image.'''
        self._check_wand_error(api.MagickDespeckleImage(self._wand))

    def edge(self, radius=0):
        ''' Enhances the edges within the image, using a convolution filter of
            the given radius.  If no radius is given, a suitable one is
            automatically chosen.

            radius = The radius of the pixel neighborhood.'''

        self._check_wand_error(api.MagickEdgeImage(self._wand, radius))

    def enhance(self):
        ''' Applies a digital filter which improves the quality of a noisy image.'''
        self._check_wand_error(api.MagickEnhanceImage(self._wand))

    def median_filter(self, radius):
        ''' Applies a digital filter that improves the quality of a noisy
            image. Each pixel is replaced by the median in a set of neighboring
            pixels as defined by radius.

            radius - The radius of the pixel neighborhood.'''
        self._check_wand_error(api.MagickMedianFilterImage(self._wand, radius))

    def equalize(self):
        ''' Equalizes the histogram of the image.'''
        self._check_wand_error(api.MagickEqualizeImage(self._wand))

    def clip(self):
        ''' Clips along the first path from the 8BIM profile, if present.'''
        self._check_wand_error(api.MagickClipImage(self._wand))

    def chop(self, size, offset):
        ''' Remove a region of the image and collapse the image to occupy the
            removed portion.

            size - A tuple describing the size of the image region.
            offset - A tuple describing the region offset.'''
        self._check_wand_error(api.MagickChopImage(self._wand, size[0], size[1], offset[0], offset[1]))

    def splice(self, size, offset):
        ''' Splice a solid colour region into the image.  This can be reversed
            by a chop.

            size - A tuple describing the size of the image region.
            offset - A tuple describing the region offset.'''
        self._check_wand_error(api.MagickSpliceImage(self._wand, size[0], size[1], offset[0], offset[1]))

    def crop(self, size, offset):
        ''' Remove a region of the image.

            size - A tuple describing the size of the image region.
            offset - A tuple describing the region offset.'''
        self._check_wand_error(api.MagickCropImage(self._wand, size[0], size[1], offset[0], offset[1]))

    def flip(self):
        ''' Creates a vertical mirror image by reflecting the pixels around the
            central x-axis.'''
        self._check_wand_error(api.MagickFlipImage(self._wand))

    def flop(self):
        ''' Creates a horizontal mirror image by reflecting the pixels around
            the central y-axis.'''
        self._check_wand_error(api.MagickFlopImage(self._wand))

    def magnify(self):
        ''' Scales the image proportionally to twice its original size.'''
        self._check_wand_error(api.MagickMagnifyImage(self._wand))

    def minify(self):
        ''' Scales the image proportionally to one-half its original size.'''
        self._check_wand_error(api.MagickMinifyImage(self._wand))

    def rotate(self, degrees, background=None):
        ''' Rotate the image.

            degrees - The number of degrees to rotate the image.
            background - The Color to use for the empty area.  Default is the
                         image's background colour, if specified, or
                         transparent if not specified.'''

        if not background:
            try:
                background = self.background_color
            except:
                background = color.TRANSPARENT

            if not background:
                background = color.TRANSPARENT

        self._check_wand_error(api.MagickRotateImage(self._wand, background._wand, degrees))

    def normalize(self):
        ''' Enhances the contrast of a color image by adjusting the pixels
            color to span the entire range of colors available.'''
        self._check_wand_error(api.MagickNormalizeImage(self._wand))

    def modulate(self, brightness=100, saturation=100, hue=100):
        ''' Lets you control the brightness, saturation, and hue of an image.
            Hue is the percentage of absolute rotation from the current position.
            For example 50 results in a counter-clockwise rotation of 90 degrees,
            150 results in a clockwise rotation of 90 degrees, with 0 and 200 both
            resulting in a rotation of 180 degrees.

            brightness - The percent change in brightness.
            saturation - The percent change in saturation.
            hue - The percent change in hue.'''
        self._check_wand_error(api.MagickModulateImage(self._wand, brightness, saturation, hue))

    def adjust_levels(self, black_point, gamma, white_point, channel=None):
        ''' Adjust the image levels by scaling the colors falling between
            specified white and black points to the full available quantum range.
            The parameters provided represent the black, mid, and white points.
            Colors darker than the black point are set to zero.  Colors
            brighter than the white point are set to the maximum quantum value.
            If a channel is given, the level adjustment is restricted to the
            specified channel.

            black_point - The darkest color in the image.
            gamma - The gamma correction to apply to the image.
            white_point - The lightest color in the image.
            channel - None, or one of RED_CHANNEL, CYAN_CHANNEL, GREEN_CHANNEL,
                      MAGENTA_CHANNEL, BLUE_CHANNEL, YELLOW_CHANNEL,
                      ALPHA_CHANNEL, OPACITY_CHANNEL, BLACK_CHANNEL,
                      INDEX_CHANNEL, ALL_CHANNELS.'''

        if channel:
            self._check_wand_error(api.MagickLevelImageChannel(self._wand, channel, black_point, gamma, white_point))
        else:
            self._check_wand_error(api.MagickLevelImage(self._wand, black_point, gamma, white_point))

    def increase_contrast(self):
        ''' Increase the differences between lighter and darker elements of the image.'''
        self._check_wand_error(api.MagickContrastImage(self._wand, 1))

    def decrease_contrast(self):
        ''' Decrease the differences between lighter and darker elements of the image.'''
        self._check_wand_error(api.MagickContrastImage(self._wand, 0))

    def gamma_correct(self, gamma, channel=None):
        ''' Gamma correct an image.  If channel is provided, the gamma
            correction is restricted to that particular channel.  

            gamma - The level of gamma correction, typically in the range of
                    0.8 to 2.3.  If a value of 0 is given and a channel is
                    specified, the influence of that channel is reduced.
            channel - None, or one of RED_CHANNEL, CYAN_CHANNEL, GREEN_CHANNEL,
                      MAGENTA_CHANNEL, BLUE_CHANNEL, YELLOW_CHANNEL,
                      ALPHA_CHANNEL, OPACITY_CHANNEL, BLACK_CHANNEL,
                      INDEX_CHANNEL, ALL_CHANNELS.'''

        if channel:
            self._check_wand_error(api.MagickGammaImageChannel(self._wand, channel, gamma))
        else:
            self._check_wand_error(api.MagickGammaImage(self._wand, gamma))

    def composite(self, image, offset, operator=None, channel=None):
        ''' Composite another image on top of this one.

            image - The Image to composite onto this one.
            offset - A tuple describing the offset of the composited image.

            operator - This operator affects how the composite is applied to
                       the image. The default is OVER_COMPOSITE_OP. Choose from
                       these operators:

                            MINUS_COMPOSITE_OP
                            ADD_COMPOSITE_OP
                            IN_COMPOSITE_OP
                            DIFFERENCE_COMPOSITE_OP
                            PLUS_COMPOSITE_OP
                            BUMPMAP_COMPOSITE_OP
                            ATOP_COMPOSITE_OP
                            XOR_COMPOSITE_OP
                            SUBTRACT_COMPOSITE_OP
                            OUT_COMPOSITE_OP
                            COPY_COMPOSITE_OP
                            DISPLACE_COMPOSITE_OP
                            OVER_COMPOSITE_OP

            channel - None, or one of RED_CHANNEL, CYAN_CHANNEL, GREEN_CHANNEL,
                      MAGENTA_CHANNEL, BLUE_CHANNEL, YELLOW_CHANNEL,
                      ALPHA_CHANNEL, OPACITY_CHANNEL, BLACK_CHANNEL,
                      INDEX_CHANNEL, ALL_CHANNELS.'''

        if not operator:
            operator = wand.OVER_COMPOSITE_OP

        _x, _y = int(offset[0]), int(offset[1])

        if channel:
            self._check_wand_error(api.MagickCompositeImageChannel(self._wand, channel, image._wand, operator, _x, _y))
        else:
            self._check_wand_error(api.MagickCompositeImage(self._wand, image._wand, operator, _x, _y))

    def quantize(self, colors, colorspace=None, tree_depth=1, dither=False, measure_error=False):
        ''' Limit the colours present in an image to a fixed amount.

            colors - The number of colors in the new image.
            colorspace - Perform color reduction in this colorspace, defaults to the image's colorspace.
            tree_depth - Default is to choose an optimal tree depth of
                         Log4(colors).  A tree of this depth generally allows
                         the best representation of the reference image with
                         the least amount of memory and the fastest
                         computational speed. In some cases, such as an image
                         with low color dispersion (a few number of colors), a
                         value other than Log4(number_colors) is required. To
                         expand the color tree completely, use a value of 8.
            dither - If True, the image is dithered.  Defaults to False.
            measure_error - If True, measures the difference between the
                            original and quantized images as an error.
                            Defaults to False.'''

        if not colorspace:
            colorspace = self.colorspace

        self._check_wand_error(api.MagickQuantizeImage(self._wand, colors, colorspace, tree_depth, dither, measure_error))

    def border(self, color, width, height):
        ''' Surraunds an image with a color defined by color.Color(color_str).'''

        self._check_wand_error(api.MagickBorderImage(self._wand, color._wand, width, height))

    def sepia_tone(self, threshold):
        ''' Applies a special effect to the image, similar to the effect
            achieved in a photo darkroom by sepia toning.  Threshold ranges from 0 to
            QuantumRange and is a measure of the extent of the sepia toning.  A threshold
            of 80 is a good starting point for a reasonable tone. '''

        self._check_wand_error(api.MagickSepiaToneImage(self._wand, threshold))

    def reduce_noise(self, radius=0):
        ''' Smooths the contours of an image while still preserving edge information. 

            The algorithm works by replacing each pixel with its neighbor
            closest in value.  A neighbor is defined by radius. Use a radius of 0 and
            reduce_noise selects a suitable radius for you.'''

        self._check_wand_error(api.MagickReduceNoiseImage(self._wand, radius))

    def add_noise(self, noise_type):
        ''' Adds random noise to the image.

            noise_type: UniformNoise, GaussianNoise, MultiplicativeNoise,
                        ImpulseNoise, LaplacianNoise, or PoissonNoise.'''

        self._check_wand_error(api.MagickAddNoiseImage(self._wand, noise_type))

    def contrast_stretch(self, black_point, white_point):
        ''' Enhances the contrast of a color image by adjusting the pixels
            color to span the entire range of colors available. '''

        self._check_wand_error(api.MagickContrastStretchImage(self._wand, black_point, white_point))

    def sigmoidal_contrast(self, sharpen, contrast, mid_point):
        ''' Adjusts the contrast of an image with a non-linear sigmoidal
            contrast algorithm.  Increase the contrast of the image using a sigmoidal
            transfer function without saturating highlights or shadows.  Contrast indicates
            how much to increase the contrast (0 is none; 3 is typical; 20 is pushing it);
            mid_point indicates where midtones fall in the resultant image (0 is white; 50
            is middle-gray; 100 is black).  Set sharpen to True to increase the image
            contrast otherwise setting it to False the contrast is reduced. '''

        self._check_wand_error(api.MagickSigmoidalContrastImage(self._wand, sharpen, contrast, mid_point))

    def evaluate(self, operator, value, channel=None):
        ''' Applies an arithmetic, relational, or logical expression to an
            image.  Use these operators to lighten or darken an image, to
            increase or decrease contrast in an image, or to produce the
            "negative" of an image.

            operator - one of: MAX_OPERATOR, MIN_OPERATOR, MULTIPLY_OPERATOR,
                       SET_OPERATOR, XOR_OPERATOR, AND_OPERATOR, ADD_OPERATOR,
                       LEFT_SHIFT_OPERATOR, RIGHT_SHIFT_OPERATOR,
                       SUBTRACT_OPERATOR, OR_OPERATOR, DIVIDE_OPERATOR.
            '''

        if channel:
            self._check_wand_error(api.MagickEvaluateImageChannel(self._wand, channel, operator, value))
        else:
            self._check_wand_error(api.MagickEvaluateImage(self._wand, operator, value))

    def unsharp_mask(self, radius, sigma, amount, threshold):
        ''' Sharpens an image. We convolve the image with a Gaussian operator
            of the given radius and standard deviation (sigma). For reasonable
            results, radius should be larger than sigma. Use a radius of 0 and
            UnsharpMaskImage() selects a suitable radius for you.

            radius
                    The radius of the Gaussian, in pixels, not counting the
                    center pixel.

            sigma
                    The standard deviation of the Gaussian, in pixels.

            amount
                    The percentage of the difference between the original and
                    the blur image that is added back into the original.

            threshold
                    The threshold in pixels needed to apply the diffence
                    amount.'''

        self._check_wand_error(api.MagickUnsharpMaskImage(self._wand, radius, sigma, amount, threshold))

    def opaque_paint(self, target, fill, fuzz=0, invert=False):
        ''' Change any pixel which matches the target to the fill.

            target  - target color to match.
            fill    - replacement color for target.
            fuzz    - Target color tolerance. Defaults to 0.
            invert  - Paint anything which doesn't match the target. Defaults to False.'''

        self._check_wand_error(api.MagickPaintOpaqueImage(self._wand, target._wand, fill._wand, fuzz, invert))

    format = property(_get_format, _set_format, None, 'The image format as a string, eg. "PNG".')
    units = property(_get_units, _set_units, None, 'The units of resolution for this image, ie. None, PIXELS_PER_INCH, PIXELS_PER_CENTIMETER.')
    resolution = property(_get_resolution, _set_resolution, None, 'A tuple containing the image resolution as expressed in image_units.')
    size = property(_get_size, scale, None, 'A tuple containing the size of the image. Setting the size is the same as calling scale().')
    colorspace = property(_get_colorspace, _set_colorspace, None, 'The image colorspace.')
    background_color = property(_get_background_color, _set_background_color, None, 'The background color of the image.')
    border_color = property(_get_border_color, _set_border_color, None, 'The border color of the image.')
    compression = property(_get_compression, _set_compression, None,
        'The image compression to use, ie. None, BZIP_COMPRESSION,\
        FAX_COMPRESSION, GROUP4_COMPRESSION, JPEG_COMPRESSION,\
        LOSSLESS_JPEG_COMPRESSION, LZW_COMPRESSION, RLE_COMPRESSION and\
        ZIP_COMPRESSION')
    compression_quality = property(_get_compression_quality, _set_compression_quality, None, 'The compression quality of the image, as a percent.')
