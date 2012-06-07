from thumbor.engines.pil import Engine as BasePilEngine
from PIL import Image
from cStringIO import StringIO

EXIF_ORIENTATAION=274

class Engine(BasePilEngine):
  def create_image(self, buffer):
        img = super(Engine,self).create_image(buffer)
        try:
            exif = img._getexif()
        except:
            return img
        orientation = None
        if exif:
            orientation = exif.get(EXIF_ORIENTATAION,1)
        
        if orientation == 2:
            # Vertical Mirror
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180
            img = img.transpose(Image.ROTATE_180)
        elif orientation == 4:
            # Horizontal Mirror
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270
            img = img.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 6:
            # Rotation 270
            img = img.transpose(Image.ROTATE_270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270
            img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:
            # Rotation 90
            img = img.transpose(Image.ROTATE_90)
        return img
