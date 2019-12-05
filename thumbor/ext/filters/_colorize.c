#include "filter.h"

#define COLORIZE(pixel,blend_percentage,colorize)  \
  (((pixel)*(100.0-(blend_percentage))+(colorize)*(blend_percentage))/100.0)

static PyObject*
_colorize_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL;
    int red_percent, green_percent, blue_percent,
        fill_red, fill_green, fill_blue;

    char *image_mode_str;

    if (!PyArg_ParseTuple(args, "siiiiiiO:apply", &image_mode_str, &red_percent, &green_percent, &blue_percent, &fill_red, &fill_green, &fill_blue, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyBytes_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyBytes_AsString(buffer);

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

        r = COLORIZE(r, red_percent, fill_red);
        g = COLORIZE(g, green_percent, fill_green);
        b = COLORIZE(b, blue_percent, fill_blue);

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
