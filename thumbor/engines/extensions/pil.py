# -*- coding: utf-8 -*-
#   Copyright (C) 2012, Almar Klein, Ant1, Marius van Voorden
#
#   This code is subject to the (new) BSD license:
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Module images2gif

Provides functionality for reading and writing animated GIF images.
Use writeGif to write a series of numpy arrays or PIL images as an
animated GIF. Use readGif to read an animated gif as a series of numpy
arrays.

Note that since July 2004, all patents on the LZW compression patent have
expired. Therefore the GIF format may now be used freely.

Acknowledgements
----------------

Many thanks to Ant1 for:
* noting the use of "palette=PIL.Image.ADAPTIVE", which significantly
  improves the results.
* the modifications to save each image with its own palette, or optionally
  the global palette (if its the same).

Many thanks to Marius van Voorden for porting the NeuQuant quantization
algorithm of Anthony Dekker to Python (See the NeuQuant class for its
license).

Many thanks to Alex Robinson for implementing the concept of subrectangles,
which (depening on image content) can give a very significant reduction in
file size.

This code is based on gifmaker (in the scripts folder of the source
distribution of PIL)


Usefull links
-------------
  * http://tronche.com/computer-graphics/gif/
  * http://en.wikipedia.org/wiki/Graphics_Interchange_Format
  * http://www.w3.org/Graphics/GIF/spec-gif89a.txt

"""
# todo: This module should be part of imageio (or at least based on)

import os

try:
    import PIL
    from PIL import Image
    from PIL.GifImagePlugin import getheader, getdata
except ImportError:
    PIL = None

try:
    import numpy as np
except ImportError:
    np = None


def get_cKDTree():
    try:
        from scipy.spatial import cKDTree
    except ImportError:
        cKDTree = None
    return cKDTree


# getheader gives a 87a header and a color palette (two elements in a list).
# getdata()[0] gives the Image Descriptor up to (including) "LZW min code size".
# getdatas()[1:] is the image data itself in chuncks of 256 bytes (well
# technically the first byte says how many bytes follow, after which that
# amount (max 255) follows).

def checkImages(images):
    """ checkImages(images)
    Check numpy images and correct intensity range etc.
    The same for all movie formats.
    """
    # Init results
    images2 = []

    for im in images:
        if PIL and isinstance(im, PIL.Image.Image):
            # We assume PIL images are allright
            images2.append(im)

        elif np and isinstance(im, np.ndarray):
            # Check and convert dtype
            if im.dtype == np.uint8:
                images2.append(im)  # Ok
            elif im.dtype in [np.float32, np.float64]:
                im = im.copy()
                im[im < 0] = 0
                im[im > 1] = 1
                im *= 255
                images2.append(im.astype(np.uint8))
            else:
                im = im.astype(np.uint8)
                images2.append(im)
            # Check size
            if im.ndim == 2:
                pass  # ok
            elif im.ndim == 3:
                if im.shape[2] not in [3, 4]:
                    raise ValueError('This array can not represent an image.')
            else:
                raise ValueError('This array can not represent an image.')
        else:
            raise ValueError('Invalid image type: ' + str(type(im)))

    # Done
    return images2


def intToBin(i):
    """ Integer to two bytes """
    # devide in two parts (bytes)
    i1 = i % 256
    i2 = int(i / 256)
    # make string (little endian)
    return chr(i1) + chr(i2)


class GifWriter:
    """ GifWriter()

    Class that contains methods for helping write the animated GIF file.

    """

    def getheaderAnim(self, im):
        """ getheaderAnim(im)

        Get animation header. To replace PILs getheader()[0]

        """
        bb = "GIF89a"
        bb += intToBin(im.size[0])
        bb += intToBin(im.size[1])
        bb += "\x87\x00\x00"
        return bb

    def getImageDescriptor(self, im, xy=None):
        """ getImageDescriptor(im, xy=None)

        Used for the local color table properties per image.
        Otherwise global color table applies to all frames irrespective of
        whether additional colors comes in play that require a redefined
        palette. Still a maximum of 256 color per frame, obviously.

        Written by Ant1 on 2010-08-22
        Modified by Alex Robinson in Janurari 2011 to implement subrectangles.

        """

        # Defaule use full image and place at upper left
        if xy is None:
            xy = (0, 0)

        # Image separator,
        bb = '\x2C'

        # Image position and size
        bb += intToBin(xy[0])  # Left position
        bb += intToBin(xy[1])  # Top position
        bb += intToBin(im.size[0])  # image width
        bb += intToBin(im.size[1])  # image height

        # packed field: local color table flag1, interlace0, sorted table0,
        # reserved00, lct size111=7=2^(7+1)=256.

        bb += '\x87'

        # LZW minimum size code now comes later, begining of [image data] blocks
        return bb

    def getAppExt(self, loops=float('inf')):
        """ getAppExt(loops=float('inf'))

        Application extention. This part specifies the amount of loops.
        If loops is 0 or inf, it goes on infinitely.

        """

        if loops == 0 or loops == float('inf'):
            loops = 2 ** 16 - 1
            # bb = "" application extension should not be used
            #         (the extension interprets zero loops
            #          to mean an infinite number of loops)
            #         Mmm, does not seem to work
        if True:
            bb = "\x21\xFF\x0B"  # application extension
            bb += "NETSCAPE2.0"
            bb += "\x03\x01"
            bb += intToBin(loops)
            bb += '\x00'  # end
        return bb

    def getGraphicsControlExt(self, duration=0.1, dispose=2):
        """ getGraphicsControlExt(duration=0.1, dispose=2)

        Graphics Control Extension. A sort of header at the start of
        each image. Specifies duration and transparancy.

        Dispose
        -------
          * 0 - No disposal specified.
          * 1 - Do not dispose. The graphic is to be left in place.
          * 2 - Restore to background color. The area used by the graphic
            must be restored to the background color.
          * 3 - Restore to previous. The decoder is required to restore the
            area overwritten by the graphic with what was there prior to
            rendering the graphic.
          * 4-7 -To be defined.

        """

        bb = '\x21\xF9\x04'
        bb += chr((dispose & 3) << 2)  # low bit 1 == transparency,
        # 2nd bit 1 == user input , next 3 bits, the low two of which are used,
        # are dispose.
        bb += intToBin(int(duration * 100))  # in 100th of seconds
        bb += '\x00'  # no transparant color
        bb += '\x00'  # end
        return bb

    def handleSubRectangles(self, images, subRectangles):
        """ handleSubRectangles(images)

        Handle the sub-rectangle stuff. If the rectangles are given by the
        user, the values are checked. Otherwise the subrectangles are
        calculated automatically.

        """

        if isinstance(subRectangles, (tuple, list)):
            # xy given directly

            # Check xy
            xy = subRectangles
            if xy is None:
                xy = (0, 0)
            if hasattr(xy, '__len__'):
                if len(xy) == len(images):
                    xy = [xxyy for xxyy in xy]
                else:
                    raise ValueError("len(xy) doesn't match amount of images.")
            else:
                xy = [xy for im in images]
            xy[0] = (0, 0)

        else:
            # Calculate xy using some basic image processing

            # Check Numpy
            if np is None:
                raise RuntimeError("Need Numpy to use auto-subRectangles.")

            # First make numpy arrays if required
            for i in range(len(images)):
                im = images[i]
                if isinstance(im, Image.Image):
                    tmp = im.convert()  # Make without palette
                    a = np.asarray(tmp)
                    if len(a.shape) == 0:
                        raise MemoryError("Too little memory to convert PIL image to array")
                    images[i] = a

            # Determine the sub rectangles
            images, xy = self.getSubRectangles(images)

        # Done
        return images, xy

    def getSubRectangles(self, ims):
        """ getSubRectangles(ims)

        Calculate the minimal rectangles that need updating each frame.
        Returns a two-element tuple containing the cropped images and a
        list of x-y positions.

        Calculating the subrectangles takes extra time, obviously. However,
        if the image sizes were reduced, the actual writing of the GIF
        goes faster. In some cases applying this method produces a GIF faster.

        """

        # Check image count
        if len(ims) < 2:
            return ims, [(0, 0) for i in ims]

        # We need numpy
        if np is None:
            raise RuntimeError("Need Numpy to calculate sub-rectangles. ")

        # Prepare
        ims2 = [ims[0]]
        xy = [(0, 0)]
        # t0 = time.time()

        # Iterate over images
        prev = ims[0]
        for im in ims[1:]:

            # Get difference, sum over colors
            diff = np.abs(im - prev)
            if diff.ndim == 3:
                diff = diff.sum(2)
            # Get begin and end for both dimensions
            X = np.argwhere(diff.sum(0))
            Y = np.argwhere(diff.sum(1))
            # Get rect coordinates
            if X.size and Y.size:
                x0, x1 = X[0], X[-1] + 1
                y0, y1 = Y[0], Y[-1] + 1
            else:  # No change ... make it minimal
                x0, x1 = 0, 2
                y0, y1 = 0, 2

            # Cut out and store
            im2 = im[y0:y1, x0:x1]
            prev = im
            ims2.append(im2)
            xy.append((x0, y0))

        # Done
        # print('%1.2f seconds to determine subrectangles of  %i images' %
        #    (time.time()-t0, len(ims2)) )
        return ims2, xy

    def convertImagesToPIL(self, images, dither, nq=0):
        """ convertImagesToPIL(images, nq=0)

        Convert images to Paletted PIL images, which can then be
        written to a single animaged GIF.

        """

        # Convert to PIL images
        images2 = []
        for im in images:
            if isinstance(im, Image.Image):
                images2.append(im)
            elif np and isinstance(im, np.ndarray):
                if im.ndim == 3 and im.shape[2] == 3:
                    im = Image.fromarray(im, 'RGB')
                elif im.ndim == 3 and im.shape[2] == 4:
                    im = Image.fromarray(im[:, :, :3], 'RGB')
                elif im.ndim == 2:
                    im = Image.fromarray(im, 'L')
                images2.append(im)

        # Convert to paletted PIL images
        images, images2 = images2, []

        # Adaptive PIL algorithm
        AD = Image.ADAPTIVE
        for im in images:
            im = im.convert('P', palette=AD, dither=dither)
            images2.append(im)

        # Done
        return images2

    def writeGifToFile(self, fp, images, durations, loops, xys, disposes):
        """ writeGifToFile(fp, images, durations, loops, xys, disposes)

        Given a set of images writes the bytes to the specified stream.

        """
        # Obtain palette for all images and count each occurance
        palettes, occur = [], []
        for im in images:
            header, usedPaletteColors = getheader(im)
            palettes.append(header[-1])  # Last part of the header is the frame palette
        for palette in palettes:
            occur.append(palettes.count(palette))

        # Select most-used palette as the global one (or first in case no max)
        globalPalette = palettes[occur.index(max(occur))]

        # Init
        frames = 0
        firstFrame = True

        for im, palette in zip(images, palettes):

            if firstFrame:
                # Write header

                # Gather info
                header = self.getheaderAnim(im)
                appext = self.getAppExt(loops)

                # Write
                fp.write(header)
                fp.write(globalPalette)
                fp.write(appext)

                # Next frame is not the first
                firstFrame = False

            if True:
                # Write palette and image data

                # Gather info
                data = getdata(im)

                imdes, data = b''.join(data[:-2]), data[-2:]
                graphext = self.getGraphicsControlExt(durations[frames], disposes[frames])
                # Make image descriptor suitable for using 256 local color palette
                lid = self.getImageDescriptor(im, xys[frames])

                # Write local header
                if (palette != globalPalette) or (disposes[frames] != 2):
                    # Use local color palette
                    fp.write(graphext)
                    fp.write(lid)  # write suitable image descriptor
                    fp.write(palette)  # write local color table
                    fp.write('\x08')  # LZW minimum size code
                else:
                    # Use global color palette
                    fp.write(graphext)
                    fp.write(imdes)  # write suitable image descriptor

                for d in data:
                    fp.write(d)

            # Prepare for next round
            frames = frames + 1

        fp.write(";")  # end gif
        return frames


# Exposed functions
def writeGif(
        filename, images, duration=0.1, repeat=True, dither=False,
        nq=0, subRectangles=True, dispose=None):
    """ writeGif(filename, images, duration=0.1, repeat=True, dither=False,
                    nq=0, subRectangles=True, dispose=None)

    Write an animated gif from the specified images.

    Parameters
    ----------
    filename : string
        The name of the file to write the image to.
    images : list
        Should be a list consisting of PIL images or numpy arrays.
        The latter should be between 0 and 255 for integer types, and
        between 0 and 1 for float types.
    duration : scalar or list of scalars
        The duration for all frames, or (if a list) for each frame.
    repeat : bool or integer
        The amount of loops. If True, loops infinitetely.
    dither : bool
        Whether to apply dithering
    nq : integer
        If nonzero, applies the NeuQuant quantization algorithm to create
        the color palette. This algorithm is superior, but slower than
        the standard PIL algorithm. The value of nq is the quality
        parameter. 1 represents the best quality. 10 is in general a
        good tradeoff between quality and speed. When using this option,
        better results are usually obtained when subRectangles is False.
    subRectangles : False, True, or a list of 2-element tuples
        Whether to use sub-rectangles. If True, the minimal rectangle that
        is required to update each frame is automatically detected. This
        can give significant reductions in file size, particularly if only
        a part of the image changes. One can also give a list of x-y
        coordinates if you want to do the cropping yourself. The default
        is True.
    dispose : int
        How to dispose each frame. 1 means that each frame is to be left
        in place. 2 means the background color should be restored after
        each frame. 3 means the decoder should restore the previous frame.
        If subRectangles==False, the default is 2, otherwise it is 1.

    """

    # Check PIL
    if PIL is None:
        raise RuntimeError("Need PIL to write animated gif files.")

    # Check images
    images = checkImages(images)

    # Instantiate writer object
    gifWriter = GifWriter()

    # Check loops
    if repeat is False:
        loops = 1
    elif repeat is True:
        loops = 0  # zero means infinite
    else:
        loops = int(repeat)

    # Check duration
    if hasattr(duration, '__len__'):
        if len(duration) == len(images):
            duration = [d for d in duration]
        else:
            raise ValueError("len(duration) doesn't match amount of images.")
    else:
        duration = [duration for im in images]

    # Check subrectangles
    if subRectangles:
        images, xy = gifWriter.handleSubRectangles(images, subRectangles)
        defaultDispose = 1  # Leave image in place
    else:
        # Normal mode
        xy = [(0, 0) for im in images]
        defaultDispose = 2  # Restore to background color.

    # Check dispose
    if dispose is None:
        dispose = defaultDispose
    if hasattr(dispose, '__len__'):
        if len(dispose) != len(images):
            raise ValueError("len(xy) doesn't match amount of images.")
    else:
        dispose = [dispose for im in images]

    # Make images in a format that we can write easy
    images = gifWriter.convertImagesToPIL(images, dither, nq)

    # Write
    fp = open(filename, 'wb')
    try:
        gifWriter.writeGifToFile(fp, images, duration, loops, xy, dispose)
    finally:
        fp.close()


def readGif(filename, asNumpy=True):
    """ readGif(filename, asNumpy=True)

    Read images from an animated GIF file.  Returns a list of numpy
    arrays, or, if asNumpy is false, a list if PIL images.

    """

    # Check PIL
    if PIL is None:
        raise RuntimeError("Need PIL to read animated gif files.")

    # Check Numpy
    if np is None:
        raise RuntimeError("Need Numpy to read animated gif files.")

    # Check whether it exists
    if not os.path.isfile(filename):
        raise IOError('File not found: ' + str(filename))

    # Load file using PIL
    pilIm = PIL.Image.open(filename)
    pilIm.seek(0)

    # Read all images inside
    images = []
    try:
        while True:
            # Get image as numpy array
            tmp = pilIm.convert()  # Make without palette
            a = np.asarray(tmp)
            if len(a.shape) == 0:
                raise MemoryError("Too little memory to convert PIL image to array")
            # Store, and next
            images.append(a)
            pilIm.seek(pilIm.tell() + 1)
    except EOFError:
        pass

    # Convert to normal PIL images if needed
    if not asNumpy:
        images2 = images
        images = []
        for im in images2:
            images.append(PIL.Image.fromarray(im))

    # Done
    return images
