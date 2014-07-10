#include "filter.h"

static PyObject*
_composite_apply(PyObject *self, PyObject *args)
{
    PyObject *py_image1 = NULL, *py_image2 = NULL, *image_mode = NULL,
             *w1, *h1, *w2, *h2, *py_x, *py_y, *py_merge = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 9, 10, &image_mode, &py_image1, &w1, &h1, &py_image2, &w2, &h2, &py_x, &py_y, &py_merge)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);

    unsigned char *ptr1 = (unsigned char *) PyString_AsString(py_image1), *aux1 = NULL;
    unsigned char *ptr2 = (unsigned char *) PyString_AsString(py_image2), *aux2 = NULL;

    int width1 = (int) PyInt_AsLong(w1),
        width2 = (int) PyInt_AsLong(w2),
        height1 = (int) PyInt_AsLong(h1),
        height2 = (int) PyInt_AsLong(h2),
        x_pos = (int) PyInt_AsLong(py_x),
        y_pos = (int) PyInt_AsLong(py_y),
        merge = 1;

    if (py_merge) {
        merge = (int) PyInt_AsLong(py_merge);
    }

    int num_bytes = bytes_per_pixel(image_mode_str);
    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B'),
        a_idx = rgb_order(image_mode_str, 'A');


    int r1, g1, b1, a1, r2, g2, b2, a2, x, y, start_x = 0, start_y = 0;

    double delta, r, g, b, a;

    if (x_pos < 0) {
        start_x = -x_pos;
        x_pos = 0;
    }
    if (y_pos < 0) {
        start_y = -y_pos;
        y_pos = 0;
    }

    for (y = start_y; y < height2; ++y) {
        if (y_pos + y >= height1) {
            break;
        }
        int line_offset1 = ((y_pos + y - start_y) * width1 * num_bytes),
            line_offset2 = (y * width2 * num_bytes);

        aux1 = ptr1 + line_offset1 + (x_pos * num_bytes);
        aux2 = ptr2 + line_offset2 + (start_x * num_bytes);

        for (x = start_x; x < width2; ++x, aux1 += num_bytes, aux2 += num_bytes) {
            if (x_pos + x >= width1) {
                break;
            }

            r1 = aux1[r_idx];
            g1 = aux1[g_idx];
            b1 = aux1[b_idx];
            a1 = aux1[a_idx];

            r2 = aux2[r_idx];
            g2 = aux2[g_idx];
            b2 = aux2[b_idx];
            a2 = aux2[a_idx];

            a1 = 255 - a1;
            a2 = 255 - a2;

            if (merge) {
                delta = (a2 / MAX_RGB_DOUBLE) * (a1 / MAX_RGB_DOUBLE);

                a = MAX_RGB_DOUBLE * delta;

                delta = 1.0 - delta;
                delta = (delta <= SMALL_DOUBLE) ? 1.0 : (1.0 / delta);

                r = delta * ALPHA_COMPOSITE_COLOR_CHANNEL(r2, a2, r1, a1);
                g = delta * ALPHA_COMPOSITE_COLOR_CHANNEL(g2, a2, g1, a1);
                b = delta * ALPHA_COMPOSITE_COLOR_CHANNEL(b2, a2, b1, a1);
            } else {
                if (a1 == 0) {
                    r = r2;
                    g = g2;
                    b = b2;
                    a = a2;
                } else {
                    r = r1;
                    g = g1;
                    b = b1;
                    a = a1;
                }
            }

            a = 255.0 - a;

            aux1[r_idx] = ADJUST_COLOR_DOUBLE(r);
            aux1[g_idx] = ADJUST_COLOR_DOUBLE(g);
            aux1[b_idx] = ADJUST_COLOR_DOUBLE(b);
            aux1[a_idx] = ADJUST_COLOR_DOUBLE(a);
        }

    }

    Py_INCREF(py_image1);
    return py_image1;
}

FILTER_MODULE(_composite,
    "apply(image_mode, buffer1, width1, height1, buffer2, width2, height2, pos_x, pos_y) -> string\n"
    "Merges two images specified by buffer1 and buffer2, taking in consideration both alpha channels."
)
