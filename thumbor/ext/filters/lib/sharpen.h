#ifndef __SHARPEN__H__
#define __SHARPEN__H__

#define CHANNELS 3

#define MAX2(x,y) ((x) > (y) ? (x) : (y))

typedef struct
{
    double sharpen_amount;
    double sharpen_radius;
    char luminance_only;
    int width, height;
    unsigned char* buffer;
    int color_offset[3]; /* offset in R, G, B order */
    int bpp;
} sharpen_info;

typedef float FLOAT;

void run_sharpen(sharpen_info *info);

#endif
