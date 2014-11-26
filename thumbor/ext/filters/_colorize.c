#include "filter.h"

#define COLORIZE(pixel,blend_percentage,colorize)  \
  (((pixel)*(100.0-(blend_percentage))+(colorize)*(blend_percentage))/100.0)

static PyObject*
_colorize_apply(PyObject *self, PyObject *args)
{
    PyObject *image_mode = NULL, *red_pct = NULL, *green_pct = NULL, *blue_pct = NULL,
             *fill_r = NULL, *fill_g = NULL, *fill_b = NULL, *buffer = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 8, 8, &image_mode, &red_pct, &green_pct, &blue_pct, &fill_r, &fill_g, &fill_b, &buffer)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int red_percent = (int) PyInt_AsLong(red_pct),
        green_percent = (int) PyInt_AsLong(green_pct),
        blue_percent = (int) PyInt_AsLong(blue_pct),
        fill_red_int = (int) PyInt_AsLong(fill_r),
        fill_green_int = (int) PyInt_AsLong(fill_g),
        fill_blue_int = (int) PyInt_AsLong(fill_b);

    int num_bytes = bytes_per_pixel(image_mode_str);

    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B'),
        i = 0, r, g, b;

    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        r = COLORIZE(r, red_percent, fill_red_int);
        g = COLORIZE(g, green_percent, fill_green_int);
        b = COLORIZE(b, blue_percent, fill_blue_int);

        ptr[i + r_idx] = ADJUST_COLOR(r);
        ptr[i + g_idx] = ADJUST_COLOR(g);
        ptr[i + b_idx] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_colorize,
    "apply(image_mode, red_pct, green_pct, blue_pct, fill_r, fill_g, fill_b, buffer) -> string"
)
