#include "filter.h"

unsigned char* get_curve(PyObject *points) {
    Py_ssize_t i, size = PyTuple_Size(points);
    unsigned char*items = (unsigned char*)malloc(size * sizeof(char) * 2);

    for (i = 0; i < size; ++i) {
        PyObject *p = PyTuple_GET_ITEM(points, i);
        items[i * 2] = (unsigned char)PyInt_AS_LONG(PyTuple_GET_ITEM(p, 0));
        items[i * 2 + 1] = (unsigned char)PyInt_AS_LONG(PyTuple_GET_ITEM(p, 1));
    }

    return items;
}

double* calculate_second_derivative(unsigned char *points, unsigned char size) {
    double* matrix = (double*)malloc(size * sizeof(double) * 3), *result = (double*)malloc(size * sizeof(double)),  *y2 = (double*)malloc(size * sizeof(double));
    int i, n = size;

    for (i = 0; i < n; i++) {
        result[i] = 0;
        matrix[i * 3] = 0;
        matrix[i * 3 + 1] = 0;
        matrix[i * 3 + 2] = 0;
    }
    matrix[1] = 1.0;


    for (i = 1; i < n - 1; i++) {
        int j = i* 2, k = i * 3;
        matrix[k] = (double)(points[j] - points[j - 2]) / 6;
        matrix[k + 1] = (double)(points[j + 2] - points[j - 2]) / 3;
        matrix[k + 2] = (double)(points[j + 2] - points[j]) /6;
        result[i] = (double)(points[j + 2 + 1] - points[j + 1]) / (points[j + 2] - points[j]) - (double)(points[j + 1] - points[j - 2 + 1]) / (points[j] - points[j - 2]);

    }

    matrix[(n - 1) * 3 + 1] = 1.0;

    for (i = 1; i < n; i++) {
        int j = i * 3;
        double k = matrix[j] / matrix[j - 3 + 1];
        matrix[j + 1] -= k * matrix[j - 3 + 2];
        matrix[j] = 0;
        result[i] -= k * result[i - 1];
    }

    for (i = n - 2; i >= 0; i--) {
        int j = i * 3;
        double k = matrix[j + 2] / matrix[j + 3 + 1];
        matrix[j + 1] -= k * matrix[j + 3];
        matrix[j + 2] = 0;
        result[i] -= k * result[i + 1];
    }

    for (i = 0; i < n; i++) {
        y2[i] = result[i] / matrix[i * 3 + 1];
    }

    free(matrix);
    free(result);
    return y2;
}

#define MINMAX(x, min, max) ((x > max) ? (max) : ((x < min) ? min : x))

unsigned char* cubic_spline_interpolation(unsigned char *points, int count_p, int size) {
    unsigned char*items = (unsigned char*)malloc(size * sizeof(char));
    double* sd = calculate_second_derivative(points, count_p);

    int i;
    for (i = 0; i < size; i ++) {
        items[i] = (unsigned char)points[1];
    }
    for (i = 0; i < count_p - 1; i++) {
        unsigned char current_x = points[i * 2], current_y = points[i * 2 + 1], next_x = points[i * 2 + 2], next_y = points[i * 2 + 2 + 1], x;
        for (x = current_x; x < next_x; x++) {
            double t = (double)(x - current_x) / (next_x - current_x),
                   a = 1 - t,
                   b = t,
                   h = next_x - current_x,
                   y = a * current_y + b * next_y + (h * h / 6) * ((a * a * a - a) * sd[i] + (b * b * b - b) * sd[i + 1]);

            items[x] = (unsigned char)(MINMAX(round(y), 0, 255));
        }
    }
    for (i = points[count_p * 2 - 2]; i<size; i++){
        items[i] = points[count_p * 2 - 1];
    }
    free(sd);
    return items;
}
static PyObject*
_curve_apply(PyObject *self, PyObject *args)
{
    char *image_mode;
    PyObject *buffer = NULL, *curve_a = NULL, *curve_r = NULL, *curve_g = NULL, *curve_b = NULL;

    if (!PyArg_ParseTuple(args, "sOOOOO:apply", &image_mode, &buffer, &curve_a, &curve_r, &curve_g, &curve_b)) {
        return NULL;
    }

    unsigned char *points_a = cubic_spline_interpolation(get_curve(curve_a), PyTuple_Size(curve_a), 256),
                  *points_r = cubic_spline_interpolation(get_curve(curve_r), PyTuple_Size(curve_r), 256),
                  *points_g = cubic_spline_interpolation(get_curve(curve_g), PyTuple_Size(curve_g), 256),
                  *points_b = cubic_spline_interpolation(get_curve(curve_b), PyTuple_Size(curve_b), 256);

    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);
    int num_bytes = bytes_per_pixel(image_mode);

    int r_idx = rgb_order(image_mode, 'R'),
        g_idx = rgb_order(image_mode, 'G'),
        b_idx = rgb_order(image_mode, 'B'),
        i = 0, r, g, b;

    size -= num_bytes;

    for (; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        r = points_r[r];
        g = points_g[g];
        b = points_b[b];

        r = points_a[r];
        g = points_a[g];
        b = points_a[b];

        ptr[i + r_idx] = ADJUST_COLOR(r);
        ptr[i + g_idx] = ADJUST_COLOR(g);
        ptr[i + b_idx] = ADJUST_COLOR(b);
    }

    free(points_a);
    free(points_r);
    free(points_g);
    free(points_b);

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_curve,
    "apply(image_mode, buffer, curve_a, curve_r, curve_g, curve_b) -> string"
)


