#include "filter.h"

static PyObject*
_round_corner_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *image_mode = NULL, *a_radius_py = NULL, *b_radius_py = NULL,
             *width_py = NULL, *height_py = NULL, *r_py = NULL, *b_py = NULL, *g_py = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 9, 9, &image_mode, &a_radius_py, &b_radius_py,
            &r_py, &g_py, &b_py, &width_py, &height_py, &buffer)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    Py_ssize_t size = PyString_Size(buffer);
    int last_pixel = size - 3;
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int a_radius = (int) PyInt_AsLong(a_radius_py),
        b_radius = (int) PyInt_AsLong(b_radius_py),
        width = (int) PyInt_AsLong(width_py),
        height = (int) PyInt_AsLong(height_py);

    unsigned char r = (unsigned char) PyInt_AsLong(r_py),
                  g = (unsigned char) PyInt_AsLong(g_py),
                  b = (unsigned char) PyInt_AsLong(b_py);

    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    float a_rad = (float)a_radius, b_rad = (float)b_radius;
    float x, y;
    for (y = 0; y <= b_rad; y += 1.0f) {
        x = -(a_rad * sqrt((b_rad * b_rad) - (y * y))) / b_rad;

        int pixel_x = 0,
            pixel_y_top = b_rad - y,
            pixel_y_bottom = (height - b_rad) + y;
        int end_x = x + a_rad;

        for (; pixel_x <= end_x; ++pixel_x) {
            int pixel_top_left = 3 * ((pixel_y_top * width) + pixel_x),
                pixel_bottom_left = 3 * ((pixel_y_bottom * width) + pixel_x),
                pixel_top_right = 3 * ((pixel_y_top * width) + (width - pixel_x)),
                pixel_bottom_right = 3 * ((pixel_y_bottom * width) + (width - pixel_x));

            if (pixel_top_left > last_pixel) {
                pixel_top_left = last_pixel;
            }
            if (pixel_bottom_left > last_pixel) {
                pixel_bottom_left = last_pixel;
            }
            if (pixel_top_right > last_pixel) {
                pixel_top_right = last_pixel;
            }
            if (pixel_bottom_right > last_pixel) {
                pixel_bottom_right = last_pixel;
            }

            if (pixel_top_left < 0) {
                pixel_top_left = 0;
            }
            if (pixel_bottom_left < 0) {
                pixel_bottom_left = 0;
            }
            if (pixel_top_right < 0) {
                pixel_top_right = 0;
            }
            if (pixel_bottom_right < 0) {
                pixel_bottom_right = 0;
            }

            ptr[pixel_top_left + r_idx] = ptr[pixel_bottom_left + r_idx] =
                ptr[pixel_top_right + r_idx] = ptr[pixel_bottom_right + r_idx] = r;
            ptr[pixel_top_left + g_idx] = ptr[pixel_bottom_left + g_idx] =
                ptr[pixel_top_right + g_idx] = ptr[pixel_bottom_right + g_idx] = g;
            ptr[pixel_top_left + b_idx] = ptr[pixel_bottom_left + b_idx] =
                ptr[pixel_top_right + b_idx] = ptr[pixel_bottom_right + b_idx] = b;

        }
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_round_corner,
    "apply(a_radius, b_radius, r, g, b, width, height, buffer) -> string"
)
