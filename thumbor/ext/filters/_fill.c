#include "filter.h"

static PyObject*
_fill_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL;
    char *image_mode_str;

    if (!PyArg_ParseTuple(args, "sO:apply", &image_mode_str, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyBytes_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyBytes_AsString(buffer);

    int num_bytes = bytes_per_pixel(image_mode_str);
    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    int i = 0, image_area = (size / num_bytes);
    unsigned long r = 0, g = 0, b = 0;

    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        r += ptr[i + r_idx];
        g += ptr[i + g_idx];
        b += ptr[i + b_idx];
    }

    r /= image_area;
    g /= image_area;
    b /= image_area;

    // TODO
    // I tried making this function return a hex color string as "23abdd"
    // but PyString_FromFormat couldnt zero pad the numbers
    // example PyString_FromFormat("%02x%02x%02x", 3, 1, 11) returns "31b"
    // the correct would be "03010b"
    // http://docs.python.org/2/c-api/string.html#PyString_FromFormat

    return Py_BuildValue("(lll)", r, g, b);
}

FILTER_MODULE(_fill,
    "apply(delta, buffer) -> string\n"
    "Auto detects the color to fill the image with, assuming "
    "'buffer' as a Python string. Returns a tuple in the format (r, g, b)."
)
