#include "filter.h"

static PyObject*
_rgb_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *delta_r = NULL, *delta_g = NULL, *delta_b = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 4, 4, &delta_r, &delta_g, &delta_b, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int delta_r_int = (int) PyInt_AsLong(delta_r),
        delta_g_int = (int) PyInt_AsLong(delta_g),
        delta_b_int = (int) PyInt_AsLong(delta_b);

    delta_r_int = (255 * delta_r_int) / 100;
    delta_g_int = (255 * delta_g_int) / 100;
    delta_b_int = (255 * delta_b_int) / 100;

    int i = 0, r, g, b;
    size -= 3;
    for (; i <= size; i += 3) {
        r = ptr[i    ];
        g = ptr[i + 1];
        b = ptr[i + 2];

        r += delta_r_int;
        g += delta_g_int;
        b += delta_b_int;

        ptr[i    ] = ADJUST_COLOR(r);
        ptr[i + 1] = ADJUST_COLOR(g);
        ptr[i + 2] = ADJUST_COLOR(b);
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_rgb,
    "apply(delta_r, delta_b, delta_g, buffer) -> string"
)
