#include "filter.h"

static PyObject*
_nine_patch_apply(PyObject *self, PyObject *args)
{
    PyObject *image_mode = NULL;
    PyObject *target_buffer = NULL;
    PyObject *target_w = NULL;
    PyObject *target_h = NULL;
    PyObject *nine_patch_buffer = NULL;
    PyObject *nine_patch_w = NULL;
    PyObject *nine_patch_h = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 7, 7, &image_mode,
            &target_buffer, &target_w, &target_h,
            &nine_patch_buffer, &nine_patch_w, &nine_patch_h)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    unsigned char *target = (unsigned char *) PyString_AsString(target_buffer);
    unsigned char *nine_patch = (unsigned char *) PyString_AsString(nine_patch_buffer);

    int tw = (int) PyInt_AsLong(target_w);
    int th = (int) PyInt_AsLong(target_h);
    int nw = (int) PyInt_AsLong(nine_patch_w);
    int nh = (int) PyInt_AsLong(nine_patch_h);

    int stride = bytes_per_pixel(image_mode_str); // typically 4 for 'RGBA'
    int alpha_idx = rgb_order(image_mode_str, 'A');

    /*
     * Currently this just pastes 'nine_patch' on top of 'target'.
     */
    int y;
    int x;
    int s; // subpixel; either r, g, b, or a
    for (y = 0; y < nh && y < th; y++) {
        for (x = 0; x < nw && x < tw; x++) {
            int t = (y * tw + x) * stride;
            int n = (y * nw + x) * stride;
            int target_alpha = 255 - target[t + alpha_idx];
            int nine_patch_alpha = 255 - nine_patch[n + alpha_idx];
            for (s = 0; s < stride; s++) {
                if (s == alpha_idx) {
                    continue;
                }
                target[t + s] = ALPHA_COMPOSITE_COLOR_CHANNEL(
                        nine_patch[n + s], nine_patch_alpha, target[t + s], target_alpha);
            }
        }
    }

    Py_INCREF(target_buffer);
    return target_buffer;
}

FILTER_MODULE(_nine_patch,
    "apply(image_mode, target_buffer, target_w, target_h, nine_patch_buffer, nine_patch_w, nine_patch_h) -> string\n"
    "Applies a nine patch..."
)
