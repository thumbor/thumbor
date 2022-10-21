#include "filter.h"

double* normalize_kernel(PyObject *kernel, Py_ssize_t size, PyObject *should_normalize) {
    Py_ssize_t i;
    double sum = 0.0;
    double *items = (double*)malloc(size * sizeof(double));

    for (i = 0; i < size; ++i) {
        PyObject *obj = PyTuple_GetItem(kernel, i);
        if (PyFloat_Check(obj)) {
            sum += (items[i] = PyFloat_AsDouble(obj));
        }
        if (PyLong_Check(obj)) {
            sum += (items[i] = (double)PyLong_AS_LONG(obj));
        }
        if (PyBytes_Check(obj)) {
            sum += (items[i] = atof(PyBytes_AsString(obj)));
        }
        if (PyUnicode_Check(obj)) {
            sum += (items[i] = atof(PyBytes_AsString(PyUnicode_AsUTF8String(obj))));
        }
    }

    if (PyObject_IsTrue(should_normalize) && sum != 0.0) {
        for (i = 0; i < size; ++i) {
            items[i] = items[i] / sum;
        }
    }

    return items;
}


#define MINMAX(x, min, max) ((x > max) ? (max) : ((x < min) ? min : x))


static PyObject*
_convolution_apply(PyObject *self, PyObject *args)
{
    char *image_mode;
    unsigned char *img_buffer, *copy_buffer;
    int columns_count;
    Py_ssize_t kernel_size = 0, width = 0, height = 0;
    PyObject *kernel_tuple, *buffer, *should_normalize;

    if (!PyArg_ParseTuple(args, "sOiiOiO:apply", &image_mode, &buffer, &width, &height, &kernel_tuple, &columns_count, &should_normalize)) {
        return NULL;
    }

    kernel_size = PyTuple_Size(kernel_tuple);
    if ((kernel_size % columns_count != 0) || (kernel_size % 2 == 0) || ((kernel_size / columns_count) % 2) == 0) {
        // TODO: error, not a valid kernel
        return NULL;
    }

    double *kernel = normalize_kernel(kernel_tuple, kernel_size, should_normalize);

    Py_ssize_t size = PyBytes_Size(buffer);
    img_buffer = (unsigned char *)PyBytes_AsString(buffer);
    copy_buffer = (unsigned char *)malloc(size * sizeof(unsigned char));
    memcpy(copy_buffer, img_buffer, size * sizeof(unsigned char));

    int num_bytes = bytes_per_pixel(image_mode);
    int r_idx = rgb_order(image_mode, 'R'),
        g_idx = rgb_order(image_mode, 'G'),
        b_idx = rgb_order(image_mode, 'B'),
        a_idx = rgb_order(image_mode, 'A');

    int rows_count = kernel_size / columns_count,
        mid_x = columns_count >> 1,
        mid_y = rows_count >> 1,
        max_width_idx = width - 1,
        max_height_idx = height - 1,
        width_bytes_count = width * num_bytes;

    int img_x, img_y, pos_x, pos_y;

    for (img_y = 0; img_y < height; ++img_y) {
        for (img_x = 0; img_x < width; ++img_x) {
            double sum_r = 0, sum_g = 0, sum_b = 0, sum_a = 0;

            for (pos_y = img_y - mid_y; pos_y <= img_y + mid_y; ++pos_y) {
                for(pos_x = img_x - mid_x; pos_x <= img_x + mid_x; ++pos_x) {
                    int kernel_x = pos_x - img_x + mid_x,
                        kernel_y = pos_y - img_y + mid_y;

                    int tmp_idx = (MINMAX(pos_y, 0, max_height_idx) * width_bytes_count) + (MINMAX(pos_x, 0, max_width_idx) * num_bytes);
                    double kernel_value = kernel[(kernel_y * columns_count) + kernel_x];
                    sum_r += copy_buffer[tmp_idx + r_idx] * kernel_value;
                    sum_g += copy_buffer[tmp_idx + g_idx] * kernel_value;
                    sum_b += copy_buffer[tmp_idx + b_idx] * kernel_value;
                    // Change alpha channel only when available
                    if (num_bytes > 3) {
                        sum_a += copy_buffer[tmp_idx + a_idx] * kernel_value;
                    }
                }
            }

            img_buffer[r_idx] = ADJUST_COLOR((int)sum_r);
            img_buffer[g_idx] = ADJUST_COLOR((int)sum_g);
            img_buffer[b_idx] = ADJUST_COLOR((int)sum_b);
            if (num_bytes > 3) {
                img_buffer[a_idx] = ADJUST_COLOR((int)sum_a);
            }
            img_buffer += num_bytes;
        }
    }

    free(kernel);
    free(copy_buffer);

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_convolution,
    "apply(image_mode, buffer) -> string\n"
)
