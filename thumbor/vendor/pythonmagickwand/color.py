from pythonmagickwand import api

class Color(object):
    ''' Represents a color, supported by a PixelWand. '''

    def __init__(self, color=None):
        ''' Create a color.  The specified color can be a name or string
            representation of a color.  Acceptable values can be found in the
            ImageMagick documentation at

                http://www.imagemagick.org/script/color.php.
        '''

        self._wand = api.NewPixelWand()

        if color:
            api.PixelSetColor(self._wand, color)

    def __del__(self):
        if self._wand and api:
            self._wand = api.DestroyPixelWand(self._wand)

    def __eq__(self, other):
        ''' Two colors are equal only if they share the same normalised color
            and alpha values.'''
        return api.IsPixelWandSimilar(self._wand, other._wand, 0)\
            and api.PixelGetAlpha(self._wand) == api.PixelGetAlpha(other._wand)

    def __ne__(self, other):
        return not self.__eq__(other)

RED = Color('red')
GREEN = Color('green')
BLUE = Color('blue')
CYAN = Color('cyan')
MAGENTA = Color('magenta')
YELLOW = Color('yellow')
WHITE = Color('white')
BLACK = Color('black')
PURPLE = Color('purple')
PINK = Color('pink')
BROWN = Color('brown')
GRAY = Color('gray')
GREY = Color('grey')
TRANSPARENT = Color('transparent')
