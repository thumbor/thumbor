
from cStringIO import StringIO

from thumbor.vendor.pythonmagickwand.image import Image
from thumbor.vendor.pythonmagickwand.wand import CUBIC_FILTER

from tornado.options import options

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine():
    
    def __init__(self):
        self.image = None
    
    def load(self, buffer):
        #loads image buffer in byte format.
        self.image = Image(StringIO(buffer))

    def resize(self, width, height):
        #resizes image
        self.image.resize((width, height), CUBIC_FILTER)

    def crop(self, left, top, right, bottom):
        #crops image
        offset_left = left
        offset_top = top
        width = right - left
        height = bottom - top
        self.image.crop(
            (int(width), int(height)),
            (int(offset_left), int(offset_top))
        )

    def flip_vertically(self):
        #flips vertically
        self.image.flip()

    def flip_horizontally(self):
        #flips horizontally
        self.image.flop()
    
    @property
    def size(self):
        # returns the image size as a tuple
        return self.image.size

    def read(self, format):
        #returns image buffer in byte format.
        img_buffer = StringIO()
        self.image.format = FORMATS[format]
        self.compression_quality = options.QUALITY
        self.image.save(img_buffer)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
