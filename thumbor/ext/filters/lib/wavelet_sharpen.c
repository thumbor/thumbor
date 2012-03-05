/*
 * HEAVILY based/copied on Marco Rossini's Wavelet sharpen GIMP plugin
 * http://registry.gimp.org/node/9836
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2+
 * as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <memory.h>

#include "image_utils.h"
#include "sharpen.h"
#include "colors.h"

// Straigth copy, style adjusted
void
hat_transform(FLOAT *temp, FLOAT *base, int st, int size, int sc)
{
    int i;
    for (i = 0; i < sc; i++) {
        temp[i] = 2 * base[st * i] + base[st * (sc - i)] + base[st * (i + sc)];
    }

    for (; i + sc < size; i++) {
        temp[i] = 2 * base[st * i] + base[st * (i - sc)] + base[st * (i + sc)];
    }

    for (; i < size; i++) {
        temp[i] = 2 * base[st * i] + base[st * (i - sc)] + base[st * (2 * size - 2 - (i + sc))];
    }
}

// Mostly straigth copy, removing references to GIMP progress updates
void
wavelet_sharpen(FLOAT *fimg[CHANNELS], int width, int height,
                double amount, double radius)
{
    FLOAT *temp, amt;
    int i, lev, lpass, hpass, size, col, row;

    size = width * height;

    temp = (FLOAT *) malloc(MAX2(width, height) * sizeof(FLOAT));

    hpass = 0;
    for (lev = 0; lev < 5; lev++) {

        lpass = ((lev & 1) + 1);
        for (row = 0; row < height; row++) {
            hat_transform(temp, fimg[hpass] + row * width, 1, width, 1 << lev);
            for (col = 0; col < width; col++) {
                fimg[lpass][row * width + col] = temp[col] * 0.25f;
            }
        }
        for (col = 0; col < width; col++) {
            hat_transform(temp, fimg[lpass] + col, width, height, 1 << lev);
            for (row = 0; row < height; row++) {
                fimg[lpass][row * width + col] = temp[row] * 0.25f;
            }
        }

        amt = (float)(amount * exp(-(lev - radius) * (lev - radius) / 1.5f) + 1.f);
        for (i = 0; i < size; i++) {
            fimg[hpass][i] -= fimg[lpass][i];
            fimg[hpass][i] *= amt;

            if (hpass) {
                fimg[0][i] += fimg[hpass][i];
            }
        }
        hpass = lpass;
    }

    for (i = 0; i < size; i++) {
        fimg[0][i] = fimg[0][i] + fimg[lpass][i];
    }

    free(temp);
}

void
run_sharpen(sharpen_info *info)
{
    FLOAT *transform_buffer[CHANNELS], *aux_buffer[CHANNELS];
    int image_area = info->width * info->height;
    int buffer_len = (int)(image_area * sizeof(FLOAT));
    int i, c, width = info->width, height = info->height, channels = CHANNELS;

    // Allocating buffers
    for (c = 0; c < channels; ++c) {
        transform_buffer[c] = malloc(buffer_len);

        // First channel will always point to transform_buffer
        if (c > 0) {
            aux_buffer[c] = malloc(buffer_len);
        }
    }

    // Filling buffers with data from the original image, colors in 0.0 - 1.0 range.
    for (i = 0; i < image_area; ++i) {
        FLOAT pixel[CHANNELS];
        int buffer_pos = i * info->bpp;

        for (c = 0; c < channels; ++c) {
            pixel[c] = (FLOAT) info->buffer[buffer_pos + c];
        }
        if (info->luminance_only) {
            rgb2ycbcr(&pixel[info->color_offset[0]], &pixel[info->color_offset[1]], &pixel[info->color_offset[2]]);
        }
        for (c = 0; c < channels; ++c) {
            transform_buffer[c][i] = pixel[c] / 255.0f;
        }
    }

    // Actually running wavelet sharpen for each channel
    for (c = 0; c < channels; ++c) {
        if (info->luminance_only && c != info->color_offset[0]) {
            continue;
        }
        aux_buffer[0] = transform_buffer[c];
        wavelet_sharpen(aux_buffer, width, height,
                        info->sharpen_amount,
                        info->sharpen_radius);
    }

    // Normalizing colors (back to rgb 0 - 255 range)
    for (i = 0; i < image_area; ++i) {
        for (c = 0; c < channels; ++c) {
           transform_buffer[c][i] = transform_buffer[c][i] * 255;
        }

        if (info->luminance_only) {
            ycbcr2rgb(&(transform_buffer[info->color_offset[0]][i]), &(transform_buffer[info->color_offset[1]][i]), &(transform_buffer[info->color_offset[2]][i]));
        }

        for (c = 0; c < channels; ++c) {
           transform_buffer[c][i] = ADJUST_COLOR(transform_buffer[c][i]);
        }
    }

    // Copying data back to our original buffer
    for (i = 0; i < image_area; ++i) {
        int buffer_pos = i * info->bpp;

        for (c = 0; c < channels; ++c) {
            info->buffer[buffer_pos + c] = transform_buffer[c][i];
        }
    }

    // Cleaning up
    for (c = 0; c < channels; ++c) {
        free(transform_buffer[c]);

        if (c > 0) {
            free(aux_buffer[c]);
        }
    }
}
