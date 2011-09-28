#include "filter.h"
#include <math.h>

static PyObject*
_contrast_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *delta = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 2, 2, &delta, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    long delta_int = PyInt_AsLong(delta);

    double delta_double = pow((delta_int + 100) / 100.0, 2);

    int i = 0;
    double r, g, b;
    size -= 3;
    for (; i <= size; i += 3) {
        r = ptr[i];
        g = ptr[i + 1];
        b = ptr[i + 2];

        r = r / 255.0;
        r -= 0.5;
        r *= delta_double;
        r += 0.5;
        r *= 255;

        g = g / 255.0;
        g -= 0.5;
        g *= delta_double;
        g += 0.5;
        g *= 255;

        b = b / 255.0;
        b -= 0.5;
        b *= delta_double;
        b += 0.5;
        b *= 255;

        r = ADJUST_COLOR(r);
        g = ADJUST_COLOR(g);
        b = ADJUST_COLOR(b);

        ptr[i] = r;
        ptr[i + 1] = g;
        ptr[i + 2] = b;
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_contrast)
