
from cStringIO import StringIO

from PIL import Image

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
        self.image = Image.open(StringIO(buffer))

    def resize(self, width, height):
        #resizes image
        self.image = self.image.resize((width, height), Image.ANTIALIAS)

    def crop(self, top, left, right, bottom):
        #crops image
        self.image = self.image.crop(
            (top,
            left,
            right,
            bottom)
        )

    def flip_vertically(self):
        #flips vertically
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        #flips horizontally
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
    
    @property
    def size(self):
        # returns the image size as a tuple
        return self.image.size

    def read(self, format):
        #returns image buffer in byte format.
        img_buffer = StringIO()
        self.image.save(img_buffer, FORMATS[format], quality=options.QUALITY)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
    