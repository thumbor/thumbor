#include "filter.h"

static PyObject*
_alpha_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *delta = NULL, *image_mode = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 3, 3, &image_mode, &delta, &buffer)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int delta_int = (int) PyInt_AsLong(delta);

    int num_bytes = bytes_per_pixel(image_mode_str),
        alpha_idx = rgb_order(image_mode_str, 'A');

    delta_int = -((255 * delta_int) / 100);

    int i = 0, alpha;
    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        alpha = ptr[i + alpha_idx];
        alpha += delta_int;
        ptr[i + alpha_idx] = ADJUST_COLOR(alpha);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_alpha,
    "apply(delta, buffer) -> string\n"
    "Applies a alpha filter assuming 'delta' as an integer value between 0 and 100."
)
