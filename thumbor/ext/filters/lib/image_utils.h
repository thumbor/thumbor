#ifndef __IMAGE_UTILS__H__
#define __IMAGE_UTILS__H__

#include <math.h>

#define ADJUST_COLOR(c) ((c > 255) ? 255 : ((c < 0) ? 0 : c))

static inline int
bytes_per_pixel(char *mode)
{
    return strlen(mode);
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
