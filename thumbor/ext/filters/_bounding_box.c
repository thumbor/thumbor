#include "filter.h"

typedef struct {
    int left;
    int top;
    int right;
    int bottom;
} box;

typedef struct {
    int width;
    int height;
    int stride;
    unsigned char *image;
} bitmap;

static inline double color_distance(unsigned char *c1, unsigned char *c2, int stride) {
    double sum = 0;
    int i;
    for (i = 0; i < stride; ++i) {
        sum += ((int)c1[i] - (int)c2[i]) * ((int)c1[i] - (int)c2[i]);
    }
    return sqrt(sum);
}

static box
find_bounding_box(bitmap *image_data, char *reference_mode, int tolerance) {
    box b = {
        image_data->width, image_data->height, 0, 0
    };
    unsigned char *pixel, *reference_pixel;
    int x, xi, y, stride = image_data->stride;

    if (strcmp(reference_mode, "top-left") == 0) {
        reference_pixel = image_data->image;
    } else { // bottom-right
        reference_pixel = image_data->image + (image_data->width * stride * (image_data->height - 1)) + (stride * (image_data->width - 1));
    }

    for (y = 0; y < image_data->height; ++y) {
        for (x = 0; x < image_data->width; ++x) {
            pixel = image_data->image + (image_data->width * stride * y) + (stride * x);
            if (color_distance(pixel, reference_pixel, stride) > tolerance) {
                if (x < b.left) {
                    b.left = x;
                }
                if (y < b.top) {
                    b.top = y;
                }
                b.bottom = y;
                break;
            }
        }
        int min_right = x > b.right ? x : b.right;
        for (xi = image_data->width - 1; xi > min_right; --xi) {
            pixel = image_data->image + (image_data->width * stride * y) + (stride * xi);
            if (color_distance(pixel, reference_pixel, stride) > tolerance) {
                if (xi > b.right) {
                    b.right = xi;
                }
                break;
            }
        }
    }

    return b;
}

static PyObject*
_bounding_box_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer_py = NULL;

    char *image_mode_str, *reference_mode;
    int width, height, tolerance;

    if (!PyArg_ParseTuple(args, "siisiO:apply", &image_mode_str, &width, &height, &reference_mode, &tolerance, &buffer_py)) {
        return NULL;
    }

    unsigned char *buffer = (unsigned char *) PyBytes_AsString(buffer_py);
    int num_bytes = bytes_per_pixel(image_mode_str);

    bitmap bitmap = {
        width,
        height,
        num_bytes,
        buffer
    };

    box b = find_bounding_box(&bitmap, reference_mode, tolerance);

    return Py_BuildValue("iiii", b.left, b.top, b.right, b.bottom);
}

FILTER_MODULE(_bounding_box,
    "apply(image_mode, width, height, reference_mode, tolerance, buffer) -> (left, top, right, bottom)\n"
    "Calculates the bounding box necessary to trim an image based on the color of "
    "one of the corners and the euclidean distance between the colors within a "
    "specified tolerance."
)
