#include "filter.h"

typedef struct
{
    int width;
    int height;
    int stride;
    int alpha_idx;
    unsigned char* buffer;
} bitmap;

int get_subpixel(bitmap *b, int x, int y, int s)
{
    int pixel = (y * b->width + x) * b->stride;
    return b->buffer[pixel + s];
}

void set_subpixel(bitmap *b, int x, int y, int s, int value)
{
    int pixel = (y * b->width + x) * b->stride;
    b->buffer[pixel + s] = value;
}

// Returns nonzero if the pixel at x,y is opaque black. That color indicates stretchiness!
int is_stretchy(bitmap *b, int x, int y)
{
    int s;
    for (s = 0; s < b->stride; s++) {
        int expected = (s == b->alpha_idx) ? 255 : 0;
        if (get_subpixel(b, x, y, s) != expected) {
            return 0;
        }
    }
    return 1;
}

// Returns the number of stretchy columns in 'b'.
int compute_stretchy_width(bitmap *b)
{
    int result = 0;
    int x;
    for (x = 1; x < b->width - 1; x++) {
        if (is_stretchy(b, x, 0) != 0) {
            result++;
        }
    }
    return result;
}

// Returns the number of stretchy rows in 'b'.
int compute_stretchy_height(bitmap *b)
{
    int result = 0;
    int y;
    for (y = 1; y < b->height - 1; y++) {
        if (is_stretchy(b, 0, y) != 0) {
            result++;
        }
    }
    return result;
}

// Returns the first pixel in the next row. That is, the next row with different stretchiness.
int next_row(bitmap *b, int y)
{
    int stretchy = is_stretchy(b, 0, y) != 0;
    int n;
    for (n = y + 1; n < b->height - 1; n++) {
        int n_stretchy = is_stretchy(b, 0, n) != 0;
        if (stretchy != n_stretchy) {
            break;
        }
    }
    return n;
}

// Returns the first pixel in the next column. That is, the next column with different stretchiness.
int next_column(bitmap *b, int x)
{
    int stretchy = is_stretchy(b, x, 0) != 0;
    int n;
    for (n = x + 1; n < b->width - 1; n++) {
        int n_stretchy = is_stretchy(b, n, 0) != 0;
        if (stretchy != n_stretchy) {
            break;
        }
    }
    return n;
}

// Computes a subpixel near (x, y) in bitmap using that pixel and 3 neighboring
// pixels on the right and below. Fractions are the weight of those neighbors:
// 0.0 means don't use the neighbor at all; 1.0 means use it completely.
int interpolate_subpixel(bitmap *bitmap, int x, int y, double x_fraction, double y_fraction, int s)
{
    int a = get_subpixel(bitmap,     x,     y, s);
    int b = get_subpixel(bitmap, x + 1,     y, s);
    int c = get_subpixel(bitmap,     x, y + 1, s);
    int d = get_subpixel(bitmap, x + 1, y + 1, s);
    if (a == b && a == c && a == d) {
        return a; // Don't do lossy math unless we're actually mixing colors.
    }
    double combined
            = a * (1 - x_fraction) * (1 - y_fraction)
            + b * (0 + x_fraction) * (1 - y_fraction)
            + c * (1 - x_fraction) * (0 + y_fraction)
            + d * (0 + x_fraction) * (0 + y_fraction);
    return ADJUST_COLOR_DOUBLE(combined);
}

// Draws a region of source into a region of target, stretching as necessary.
// This uses bilinear interpolation to scale images.
void paste_rectangle(bitmap *source, int sx, int sy, int sw, int sh,
        bitmap *target, int tx, int ty, int tw, int th)
{
    if (tx + tw > target->width || ty + th > target->height) {
        return; // If the region won't fit, give up!
    }

    double x_ratio = ((double) sw - 1) / tw;
    double y_ratio = ((double) sh - 1) / th;

    int y;
    for (y = 0; y < th; y++) {
        int source_y = (int) (y_ratio * y);
        double y_fraction = (y_ratio * y) - source_y;
        int x;
        for (x = 0; x < tw; x++) {
            int source_x = (int) (x_ratio * x);
            double x_fraction = (x_ratio * x) - source_x;

            int source_alpha = 255 - interpolate_subpixel(
                    source, sx + source_x, sy + source_y, x_fraction, y_fraction, source->alpha_idx);
            int target_alpha = 255 - get_subpixel(target, tx + x, ty + y, target->alpha_idx);

            int s;
            for (s = 0; s < source->stride; s++) {
                if (s == source->alpha_idx) {
                    continue;
                }
                int source_value = interpolate_subpixel(
                        source, sx + source_x, sy + source_y, x_fraction, y_fraction, s);
                int target_value = get_subpixel(target, tx + x, ty + y, s);
                double pixel = ALPHA_COMPOSITE_COLOR_CHANNEL(source_value, source_alpha, target_value, target_alpha);
                set_subpixel(target, tx + x, ty + y, s, ADJUST_COLOR_DOUBLE(pixel));
            }
        }
    }
}

void unpack_bitmap(bitmap *bitmap, PyObject *image_mode,
        PyObject *buffer, PyObject *width, PyObject *height)
{
    char *image_mode_str = PyString_AsString(image_mode);
    bitmap->buffer = (unsigned char *) PyString_AsString(buffer);
    bitmap->width = (int) PyInt_AsLong(width);
    bitmap->height = (int) PyInt_AsLong(height);
    bitmap->stride = bytes_per_pixel(image_mode_str); // typically 4 for 'RGBA'
    bitmap->alpha_idx = rgb_order(image_mode_str, 'A');
}

// Returns a tuple of (left, top, right, bottom) containing the padding encoded
// in the nine patch. The padding is the number of non-black pixels along the
// right or bottom edge of the image. This does not include the corner pixel.
static PyObject*
_get_padding(PyObject *self, PyObject *args)
{
    PyObject *image_mode = NULL;
    PyObject *nine_patch_buffer = NULL;
    PyObject *nine_patch_w = NULL;
    PyObject *nine_patch_h = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 4, 4, &image_mode,
            &nine_patch_buffer, &nine_patch_w, &nine_patch_h)) {
        return NULL;
    }

    bitmap nine_patch;
    unpack_bitmap(&nine_patch, image_mode, nine_patch_buffer, nine_patch_w, nine_patch_h);

    int left = 0, top = 0, right = 0, bottom = 0;
    int x, y;
    for (x = 1; x < nine_patch.width - 1; x++) {
        if (is_stretchy(&nine_patch, x, nine_patch.height - 1)) {
            left = x - 1;
            break;
        }
    }
    for (x = nine_patch.width - 2; x >= 1; x--) {
        if (is_stretchy(&nine_patch, x, nine_patch.height - 1)) {
            right = nine_patch.width - 2 - x;
            break;
        }
    }
    for (y = 1; y < nine_patch.height - 1; y++) {
        if (is_stretchy(&nine_patch, nine_patch.width - 1, y)) {
            top = y - 1;
            break;
        }
    }
    for (y = nine_patch.height- 2; y >= 1; y--) {
        if (is_stretchy(&nine_patch, nine_patch.width - 1, y)) {
            bottom = nine_patch.height - 2 - y;
            break;
        }
    }

    return Py_BuildValue("iiii", left, top, right, bottom);
}

static PyObject*
_nine_patch_apply(PyObject *self, PyObject *args)
{
    // The image mode, which must apply to both bitmaps.
    PyObject *image_mode = NULL;

    // The target to draw into.
    PyObject *target_buffer = NULL;
    PyObject *target_w = NULL;
    PyObject *target_h = NULL;

    // The nine patch to use as a frame.
    PyObject *nine_patch_buffer = NULL;
    PyObject *nine_patch_w = NULL;
    PyObject *nine_patch_h = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 7, 7, &image_mode,
            &target_buffer, &target_w, &target_h,
            &nine_patch_buffer, &nine_patch_w, &nine_patch_h)) {
        return NULL;
    }

    bitmap target;
    unpack_bitmap(&target, image_mode, target_buffer, target_w, target_h);

    bitmap nine_patch;
    unpack_bitmap(&nine_patch, image_mode, nine_patch_buffer, nine_patch_w, nine_patch_h);

    // The number of stretchy pixels in the source.
    int source_stretchy_width = compute_stretchy_width(&nine_patch);
    int source_stretchy_height = compute_stretchy_height(&nine_patch);

    // The number of fixed pixels in the source and target.
    int fixed_width = nine_patch.width - 2 - source_stretchy_width;
    int fixed_height = nine_patch.height - 2 - source_stretchy_height;

    // The number of target pixels to be shared by all stretchy regions.
    int target_stretchy_width = target.width - fixed_width;
    int target_stretchy_height = target.height - fixed_height;
    if (target_stretchy_width < 0) {
        target_stretchy_width = 0;
    }
    if (target_stretchy_height < 0) {
        target_stretchy_height = 0;
    }

    /*
     * Cut the image into rows and columns, each axis alternating between
     * stretchy and non-stretchy. This walks through the rows from top to
     * bottom. Within each row it walks through the columns left to right.
     * It computes the size & location of each cell in both the nine patch and
     * the target image. Then it pastes one cell over the other, stretching the
     * source image as necessary.
     */
    int source_y = 1;
    int target_y = 0;
    while (source_y < nine_patch.height - 1) {
        int row_stretchy = is_stretchy(&nine_patch, 0, source_y);
        int source_height = next_row(&nine_patch, source_y) - source_y;
        int target_height = (row_stretchy != 0)
                ? (int) ((double) source_height / source_stretchy_height * target_stretchy_height + 0.5)
                : source_height;

        int source_x = 1;
        int target_x = 0;
        while (source_x < nine_patch.width - 1) {
            int col_stretchy = is_stretchy(&nine_patch, source_x, 0);
            int source_width = next_column(&nine_patch, source_x) - source_x;
            int target_width = (col_stretchy != 0)
                    ? (int) ((double) source_width / source_stretchy_width * target_stretchy_width + 0.5)
                    : source_width;
            paste_rectangle(&nine_patch, source_x, source_y, source_width, source_height,
                    &target, target_x, target_y, target_width, target_height);
            target_x += target_width;
            source_x += source_width;
        }

        target_y += target_height;
        source_y += source_height;
    }

    Py_INCREF(target_buffer);
    return target_buffer;
}

static PyMethodDef _nine_patch_methods[] = {
    {"apply", _nine_patch_apply, METH_VARARGS, NULL},
    {"get_padding", _get_padding, METH_VARARGS, NULL},
    { 0, 0, 0, 0 }
};

PyMODINIT_FUNC init_nine_patch(void) {
    Py_InitModule3("_nine_patch", _nine_patch_methods, "_nine_patch native module");
}
