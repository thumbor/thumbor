#include "filter.h"

static PyObject*
_equalize_apply(PyObject *self, PyObject *args)
{
    PyObject *buffer = NULL, *image_mode = NULL;

    if (!PyArg_UnpackTuple(args, "apply", 2, 2, &image_mode, &buffer)) {
        return NULL;
    }

    char *image_mode_str = PyString_AsString(image_mode);
    Py_ssize_t original_size = PyString_Size(buffer);
    Py_ssize_t size = PyString_Size(buffer);
    unsigned char *ptr = (unsigned char *) PyString_AsString(buffer);

    int num_bytes = bytes_per_pixel(image_mode_str);
    int area = (int)(size / num_bytes);

    int r_idx = rgb_order(image_mode_str, 'R'),
        g_idx = rgb_order(image_mode_str, 'G'),
        b_idx = rgb_order(image_mode_str, 'B');

    int redHist[256] = {0};
    int redCumFreq[256] = {0};
    int greenHist[256] = {0};
    int greenCumFreq[256] = {0};
    int blueHist[256] = {0};
    int blueCumFreq[256] = {0};

    int i = 0, r, g, b;
    size -= num_bytes;
    for (; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        redHist[r]++;
        greenHist[g]++;
        blueHist[b]++;
    }

    int rCum = 0, gCum = 0, bCum = 0;
    for(i = 0; i < 256; i++) {
        rCum += redHist[i];
        gCum += greenHist[i];
        bCum += blueHist[i];

        if (redHist[i] > 0) {
            redCumFreq[i] = rCum;
        }
        if (greenHist[i] > 0) {
            greenCumFreq[i] = gCum;
        }
        if (blueHist[i] > 0) {
            blueCumFreq[i] = bCum;
        }
    }

    int rMinCdf=0, gMinCdf=0, bMinCdf=0;
    i = 0;
    while (rMinCdf == 0 && gMinCdf == 0 && bMinCdf == 0 && i < 256) {
        if (rMinCdf == 0 && redCumFreq[i] != 0) {
            rMinCdf = redCumFreq[i];
        }
        if (gMinCdf == 0 && greenCumFreq[i] != 0) {
            gMinCdf = greenCumFreq[i];
        }
        if (bMinCdf == 0 && blueCumFreq[i] != 0) {
            bMinCdf = blueCumFreq[i];
        }
        i++;
    }

    size = original_size;
    size -= num_bytes;
    for (i = 0; i <= size; i += num_bytes) {
        r = ptr[i + r_idx];
        g = ptr[i + g_idx];
        b = ptr[i + b_idx];

        // Refer to http://en.wikipedia.org/wiki/Histogram_equalization
        float rColor = (((float)redCumFreq[r] - rMinCdf) / (area - rMinCdf)) * 255.0f;
        float gColor = (((float)greenCumFreq[g] - gMinCdf) / (area - gMinCdf)) * 255.0f;
        float bColor = (((float)blueCumFreq[b] - bMinCdf) / (area - bMinCdf)) * 255.0f;

        ptr[i + r_idx] = rColor;
        ptr[i + g_idx] = gColor;
        ptr[i + b_idx] = bColor;
    }

    Py_INCREF(buffer);
    return buffer;
}

FILTER_MODULE(_equalize,
    "apply(buffer) -> string\n"
    "Applies a histogram equalization algorithm filter"
    "assuming 'buffer' as a Python string. Returns the modified buffer."
)
