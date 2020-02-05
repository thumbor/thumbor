#include "filter.h"

static PyObject*
_rgb_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL;
    char *image_mode_str;
    int delta_r_int, delta_g_int, delta_b_int;

    if (!PyArg_ParseTuple(args, "siiiO:apply", &image_mode_str, &delta_r_int, &delta_g_int, &delta_b_int, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyBytes_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyBytes_AsString(buffer);

    int num_bytes = bytes_per_pixel(image_mode_str);

    delta_r_int = (255 * delta_r_int) / 100;
    delta_g_int = (255 * delta_g_int) / 100;
    delta_b_int = (255 * delta_b_int) / 100;

    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B'),
        i = 0, r, g, b;

    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        r += delta_r_int;
        g += delta_g_int;
        b += delta_b_int;

        ptr[i + r_idx] = ADJUST_COLOR(r);
        ptr[i + g_idx] = ADJUST_COLOR(g);
        ptr[i + b_idx] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_rgb,
    "apply(image_mode, delta_r, delta_b, delta_g, buffer) -> string"
)
