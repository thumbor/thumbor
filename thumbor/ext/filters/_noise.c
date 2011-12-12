#include "filter.h"

static PyObject*
_noise_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *amount = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 2, 2, &amount, &buffer)) {
        return NULL;
    }

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int amount_int = (int) PyInt_AsLong(amount);

    if (amount_int > 0) {
        int i = 0, pixel_component, rand_val;
        size -= 3;
        for (; i <= size; ++i) {
            rand_val = (rand() % amount_int) - (amount_int >> 1);
            pixel_component = ptr[i] + rand_val;

            ptr[i] = ADJUST_COLOR(pixel_component);
        }
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_noise,
    "apply(delta, buffer) -> string\n"
    "Adds noise to the image, assuming amount as an integer between 0 and 100, "
    "and 'buffer' as a Python string. Returns the received buffer."
)
