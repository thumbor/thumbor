#include "filter.h"

static PyObject*
_contrast_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL;
    char *image_mode_str;
    int delta_int;

    if (!PyArg_ParseTuple(args, "siO:apply", &image_mode_str, &delta_int, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyBytes_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyBytes_AsString(buffer);

    int num_bytes = bytes_per_pixel(image_mode_str);
    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    delta_int = delta_int + 100;
    delta_int = (delta_int * delta_int) / 100;

    int i = 0, r, g, b;
    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        r = ((delta_int * (r - 128)) / 100) + 128;
        g = ((delta_int * (g - 128)) / 100) + 128;
        b = ((delta_int * (b - 128)) / 100) + 128;

        ptr[i + r_idx] = ADJUST_COLOR(r);
        ptr[i + g_idx] = ADJUST_COLOR(g);
        ptr[i + b_idx] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_contrast,
    "apply(delta, buffer) -> string\n"
    "Applies a contrast filter assuming 'delta' as an integer value between -100 and 100, "
    "and 'buffer' as a Python string. Returns the received buffer."
)
