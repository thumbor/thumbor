#include "filter.h"
#include "sharpen.h"

static PyObject*
_sharpen_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer_py;

    char *image_mode_str;
    int width, height;

    double amount_double, radius_double;

    char luminance_only_bool;

    if (!PyArg_ParseTuple(args, "siiddBO:apply", &image_mode_str, &width, &height, &amount_double, &radius_double, &luminance_only_bool, &buffer_py)) {
        return NULL;
    }

    unsigned char *buffer = (unsigned char *) PyBytes_AsString(buffer_py);

    int num_bytes = bytes_per_pixel(image_mode_str);
    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    sharpen_info info = {
      amount_double,
      radius_double,
      luminance_only_bool,
      width, height,
      buffer,
      {r_idx, g_idx, b_idx},
      num_bytes
    };

    run_sharpen(&info);

    Py_INCREF(buffer_py);
    return buffer_py;
}

FILTER_MODULE(_sharpen,
    "apply(image_mode, width, height, amount, radius, luminance_only, buffer) -> string"
)
