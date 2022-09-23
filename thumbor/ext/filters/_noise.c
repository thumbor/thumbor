#include "filter.h"

static PyObject*
_noise_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL;
    char *image_mode_str;
    int amount_int, seed_int;

    if (!PyArg_ParseTuple(args, "siO|i:apply", &image_mode_str, &amount_int, &buffer, &seed_int)) {
        return NULL;
    }

    Py_ssize_t size = PyBytes_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyBytes_AsString(buffer);

    int num_bytes = bytes_per_pixel(image_mode_str);
    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    if (amount_int > 0) {
        int i = 0, r, g, b, rand_val;
        size -= num_bytes;

        if (seed_int > 0) {
            srandom(seed_int);
        }

        for (; i <= size; i += num_bytes) {
            rand_val = (random() % amount_int) - (amount_int >> 1);

            r = ptr[i + r_idx];
            g = ptr[i + g_idx];
            b = ptr[i + b_idx];

            r += rand_val;
            g += rand_val;
            b += rand_val;

            ptr[i + r_idx] = ADJUST_COLOR(r);
            ptr[i + g_idx] = ADJUST_COLOR(g);
            ptr[i + b_idx] = ADJUST_COLOR(b);
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
