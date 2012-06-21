#ifndef __IMAGE_UTILS__H__
#define __IMAGE_UTILS__H__

#include <math.h>

#define MAX_RGB_DOUBLE 255.0
#define MAX_RGB 255
#define SMALL_DOUBLE 1.0e-12

#define ADJUST_COLOR(c) ((c > MAX_RGB) ? MAX_RGB : ((c < 0) ? 0 : c))
#define ADJUST_COLOR_DOUBLE(c) ((int)((c > MAX_RGB_DOUBLE) ? MAX_RGB : ((c < 0.0) ? 0 : c)))

#define ALPHA_COMPOSITE_COLOR_CHANNEL(color1, alpha1, color2, alpha2) \
    ( ((1.0 - (alpha1 / MAX_RGB_DOUBLE)) * (double) color1) + \
      ((1.0 - (alpha2 / MAX_RGB_DOUBLE)) * (double) color2 * (alpha1 / MAX_RGB_DOUBLE)) )


static inline int
bytes_per_pixel(char *mode)
{
    return (int) strlen(mode);
}

static inline int
rgb_order(char *mode, char color)
{
    int i = 0;
    while (*mode != color && *(++mode)) {
        ++i;
    }
    return i;
}

#endif
