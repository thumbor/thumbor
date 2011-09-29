#include "filter.h"

static PyObject*
_brightness_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *delta = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 2, 2, &delta, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int delta_int = (int) PyInt_AsLong(delta);

    delta_int = (255 * delta_int) / 100;

    int i = 0, r, g, b;
    size -= 3;
    for (; i <= size; i += 3) {
        r = ptr[i];
        g = ptr[i + 1];
        b = ptr[i + 2];

        r += delta_int;
        g += delta_int;
        b += delta_int;

        ptr[i] = ADJUST_COLOR(r);
        ptr[i + 1] = ADJUST_COLOR(g);
        ptr[i + 2] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_brightness,
    "apply(delta, buffer) -> string\n"
    "Applies a brightness filter assuming 'delta' as an integer value between -100 and 100, "
    "and 'buffer' as a Python string. Returns the received buffer."
)
