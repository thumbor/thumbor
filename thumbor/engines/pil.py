
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
    
    def load(self, buffer):
        #loads image buffer in byte format.
        self.image = Image.open(StringIO(buffer))

    def resize(self, width, height):
        self.image = self.image.resize((int(width), int(height)), Image.ANTIALIAS)

    def crop(self, left, top, right, bottom):
        self.image = self.image.crop(
            (int(left),
            int(top),
            int(right),
            int(bottom))
        )

    def flip_vertically(self):
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def flip_horizontally(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
    
    @property
    def size(self):
        # returns the image size as a tuple
        return self.image.size

    def read(self, extension):
        #returns image buffer in byte format.
        img_buffer = StringIO()
        self.image.save(img_buffer, FORMATS[extension], quality=options.QUALITY)
        results = img_buffer.getvalue()
        img_buffer.close()
        return results
    