#include "filter.h"

static PyObject*
_round_corner_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *image_mode = NULL, *a_radius_py = NULL, *b_radius_py = NULL,
             *width_py = NULL, *height_py = NULL, *r_py = NULL, *b_py = NULL, *g_py = NULL,
             *aa_py = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 10, 10, &aa_py, &image_mode, &a_radius_py, &b_radius_py,
            &r_py, &g_py, &b_py, &width_py, &height_py, &buffer)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    int aa_enabled = (int)PyInt_AsLong(aa_py);

    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int a_radius = (int) PyInt_AsLong(a_radius_py),
        b_radius = (int) PyInt_AsLong(b_radius_py),
        width = (int) PyInt_AsLong(width_py),
        height = (int) PyInt_AsLong(height_py);

    unsigned char r = (unsigned char) PyInt_AsLong(r_py),
                  g = (unsigned char) PyInt_AsLong(g_py),
                  b = (unsigned char) PyInt_AsLong(b_py);

    int num_bytes = bytes_per_pixel(image_mode_str);

    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    float aa_amount = .75f;

    if (a_radius > width / 2) {
        a_radius = width / 2;
    }
    if (b_radius > height / 2) {
        b_radius = height / 2;
    }

    float a_rad = (float)a_radius, b_rad = (float)b_radius;
    float x;
    int y = 0;

    #ifndef NDEBUG
    int image_size = width * height * num_bytes;
    #endif

    for (y = 0; y <= b_rad; y += 1) {
        x = (float)(-(a_rad * sqrt((b_rad * b_rad) - (y * y))) / b_rad);

        int curr_x = 0,
            y_top = b_rad - y,
            y_bottom = (height - b_rad) + y - 1;
        int end_x = x + a_rad;

        for (; curr_x < end_x; ++curr_x) {
            int top_left = num_bytes * ((y_top * width) + curr_x),
                bottom_left = num_bytes * ((y_bottom * width) + curr_x),
                top_right = num_bytes * ((y_top * width) + (width - curr_x)),
                bottom_right = num_bytes * ((y_bottom * width) + (width - curr_x));

            assert(top_left + r_idx < image_size);
            assert(top_left + g_idx < image_size);
            assert(top_left + b_idx < image_size);
            assert(bottom_left + r_idx < image_size);
            assert(bottom_left + g_idx < image_size);
            assert(bottom_left + b_idx < image_size);
            ptr[top_left + r_idx] = ptr[bottom_left + r_idx] = r;
            ptr[top_left + g_idx] = ptr[bottom_left + g_idx] = g;
            ptr[top_left + b_idx] = ptr[bottom_left + b_idx] = b;

            if (curr_x > 0) {
                assert(top_right + r_idx < image_size);
                assert(top_right + g_idx < image_size);
                assert(top_right + b_idx < image_size);
                assert(bottom_right + r_idx < image_size);
                assert(bottom_right + g_idx < image_size);
                assert(bottom_right + b_idx < image_size);
                ptr[top_right + r_idx] = ptr[bottom_right + r_idx] = r;
                ptr[top_right + g_idx] = ptr[bottom_right + g_idx] = g;
                ptr[top_right + b_idx] = ptr[bottom_right + b_idx] = b;
            }
        }

        if (!aa_enabled) {
            continue;
        }

        int last_top_left = num_bytes * ((y_top * width) + end_x),
            last_bottom_left = num_bytes * ((y_bottom * width) + end_x),
            last_top_right = num_bytes * ((y_top * width) + (width - end_x)),
            last_bottom_right = num_bytes * ((y_bottom * width) + (width - end_x));

        int idx = 1;
        int aa_x = x - 1;
        unsigned char *color_top_left = ptr + last_top_left,
                      *color_bottom_left = ptr + last_bottom_left,
                      *color_top_right = ptr + last_top_right,
                      *color_bottom_right = ptr + last_bottom_right;


        int pixel_count_x = 0;

        for (; aa_x >= (-a_rad); --aa_x) {
            int aa_y = (float)(((b_rad * sqrt(a_rad * a_rad - aa_x * aa_x)) / a_rad) + 1.f);

            if (aa_y != y) {
                break;
            }

            ++pixel_count_x;
        }

        aa_x = x - pixel_count_x;
        if (aa_x < -a_rad) {
            aa_x += 1;
        }
        idx = 1;
        for (; aa_x < x; ++aa_x, ++idx) {
            int aa_x_adj = aa_x + a_rad;
            int top_left = num_bytes * ((y_top * width) + aa_x_adj),
                bottom_left = num_bytes * ((y_bottom * width) + aa_x_adj),
                top_right = num_bytes * ((y_top * width) + (width - aa_x_adj)),
                bottom_right = num_bytes * ((y_bottom * width) + (width - aa_x_adj));


            float aa = 1.f - ((idx / (float)pixel_count_x) * aa_amount);

            ptr[top_left + r_idx] = (color_top_left[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[top_left + g_idx] = (color_top_left[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[top_left + b_idx] = (color_top_left[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[bottom_left + r_idx] = (color_bottom_left[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[bottom_left + g_idx] = (color_bottom_left[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[bottom_left + b_idx] = (color_bottom_left[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[top_right + r_idx] = (color_top_right[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[top_right + g_idx] = (color_top_right[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[top_right + b_idx] = (color_top_right[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[bottom_right + r_idx] = (color_bottom_right[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[bottom_right + g_idx] = (color_bottom_right[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[bottom_right + b_idx] = (color_bottom_right[b_idx] * (1.f - aa)) + (b * (aa));
        }

    }

    if (!aa_enabled) {
        goto END;
    }

    for (x = 0.f; x >= -a_rad; x -= 1.f) {
        float y = (float)((b_rad * sqrt((a_rad * a_rad) - (x * x))) / a_rad);

        int pixel_count_y = 0;
        int aa_y = y + 1;
        for (; aa_y < b_rad; ++aa_y) {
            int aa_x = (float)(-((a_rad * sqrt((b_rad * b_rad) - (aa_y * aa_y))) / b_rad) - 1.f);
            if (aa_x != (int)x) {
                break;
            }

            ++pixel_count_y;
        }

        int end_x = x + a_rad;
        int y_top = b_rad - y;
        int y_bottom = (height - b_rad) + y - 1;

        int last_top_left = num_bytes * ((y_top * width) + end_x),
            last_bottom_left = num_bytes * ((y_bottom * width) + end_x),
            last_top_right = num_bytes * ((y_top * width) + (width - end_x)),
            last_bottom_right = num_bytes * ((y_bottom * width) + (width - end_x));

        unsigned char *color_top_left = ptr + last_top_left,
                      *color_bottom_left = ptr + last_bottom_left,
                      *color_top_right = ptr + last_top_right,
                      *color_bottom_right = ptr + last_bottom_right;

        int left_x = x + a_rad;
        int right_x = width - a_rad - x;
        int idx = 1;

        aa_y = y + pixel_count_y;
        if (aa_y > b_rad) {
            aa_y -= 1;
        }
        for (; aa_y > y; --aa_y, ++idx) {
            int top_left = num_bytes * (((b_rad - aa_y) * width) + left_x),
                bottom_left = num_bytes * ((((height - b_rad) + aa_y - 1) * width) + left_x),
                top_right = num_bytes * (((b_rad - aa_y) * width) + right_x),
                bottom_right = num_bytes * ((((height - b_rad) + aa_y - 1) * width) + right_x);

            float aa = 1.f - ((idx / (float)pixel_count_y) * aa_amount);

            ptr[top_left + r_idx] = (color_top_left[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[top_left + g_idx] = (color_top_left[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[top_left + b_idx] = (color_top_left[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[bottom_left + r_idx] = (color_bottom_left[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[bottom_left + g_idx] = (color_bottom_left[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[bottom_left + b_idx] = (color_bottom_left[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[top_right + r_idx] = (color_top_right[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[top_right + g_idx] = (color_top_right[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[top_right + b_idx] = (color_top_right[b_idx] * (1.f - aa)) + (b * (aa));

            ptr[bottom_right + r_idx] = (color_bottom_right[r_idx] * (1.f - aa)) + (r * (aa));
            ptr[bottom_right + g_idx] = (color_bottom_right[g_idx] * (1.f - aa)) + (g * (aa));
            ptr[bottom_right + b_idx] = (color_bottom_right[b_idx] * (1.f - aa)) + (b * (aa));
        }
    }

END:

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_round_corner,
    "apply(a_radius, b_radius, r, g, b, width, height, buffer) -> string"
)
