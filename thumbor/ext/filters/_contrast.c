#include "filter.h"

static PyObject*
_contrast_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *delta = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 2, 2, &delta, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int delta_int = (int) PyInt_AsLong(delta);

    delta_int = delta_int + 100;
    delta_int = (delta_int * delta_int) / 100;

    int i = 0, r, g, b;
    size -= 3;
    for (; i <= size; i += 3) {
        r = ptr[i];
        g = ptr[i + 1];
        b = ptr[i + 2];

        r = ((delta_int * (r - 128)) / 100) + 128;
        g = ((delta_int * (g - 128)) / 100) + 128;
        b = ((delta_int * (b - 128)) / 100) + 128;

        ptr[i] = ADJUST_COLOR(r);
        ptr[i + 1] = ADJUST_COLOR(g);
        ptr[i + 2] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_contrast)
