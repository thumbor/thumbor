#include "filter.h"
#include "sharpen.h"

static PyObject*
_sharpen_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer_py = NULL, *image_mode = NULL, *amount = NULL, *radius = NULL,
             *luminance_only = NULL, *width_py = NULL, *height_py = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 7, 7, &image_mode, &width_py, &height_py, &amount, &radius, &luminance_only, &buffer_py)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    unsigned char *buffer = (unsigned char *) PyString_AsString(buffer_py);
    double amount_double = PyFloat_AsDouble(amount),
           radius_double = PyFloat_AsDouble(radius);

    char luminance_only_bool = (char) PyObject_IsTrue(luminance_only);

    int width = (int) PyInt_AsLong(width_py),
        height = (int) PyInt_AsLong(height_py);

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
