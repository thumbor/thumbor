
from cStringIO import StringIO

from thumbor.vendor.pythonmagickwand.image import Image
from thumbor.vendor.pythonmagickwand import wand

from tornado.options import options

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}

class Engine():
    
    def load(self, buffer):
        #loads image buffer in byte format.
        self.image = Image(StringIO(buffer))

    def resize(self, width, height):
        self.image.resize((int(width), int(height)), wand.CATROM_FILTER, 1)

    def crop(self, left, top, right, bottom):
        offset_left = left
        offset_top = top
        width = right - left
        height = bottom - top
        self.image.crop(
            (int(width), int(height)),
            (int(offset_left), int(offset_top))
        )

    def flip_vertically(self):
        self.image.flip()

    def flip_horizontally(self):
        self.image.flop()
    
    def tostring(self):
        return self.image.tostring()
    
    @property
    def size(self):
        # returns the image size as a tuple
        return self.image.size

    def read(self, extension):
        #returns image buffer in byte format.
        img_buffer = StringIO()
        self.image.format = FORMATS[extension]
        self.image.compression_quality = options.QUALITY
        self.image.save(img_buffer)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
