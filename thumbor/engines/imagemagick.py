
from cStringIO import StringIO

from pythonmagickwand.image import Image

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
        self.image.resize((width, height), 'CUBIC')

    def crop(self, left, top, right, bottom):
        #crops image
        offset_left = left
        offset_top = top
        width = right - left
        height = bottom - top
        self.image.crop(
            (width,
            height,
            offset_left,
            offset_top)
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
        self.image.save(img_buffer, quality=options.QUALITY)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
