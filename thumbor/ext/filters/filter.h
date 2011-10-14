#ifndef __FILTER__H__
#define __FILTER__H__

#include <Python.h>

#include <math.h>

#define RGB_LENGTH 3

#define ADJUST_COLOR(c) ((c > 255) ? 255 : ((c < 0) ? 0 : c))

#define FILTER_MODULE(NAME, DOC)    static PyMethodDef NAME ## _methods[] = { \
                                        {"apply", NAME ## _apply, METH_VARARGS, DOC}, \
                                        {0, 0, 0, 0} \
                                    }; \
                                    PyMODINIT_FUNC init ## NAME(void) { \
                                        Py_InitModule3(#NAME, NAME ## _methods, #NAME " native module"); \
                                    }

static inline int
rgb_order(char *mode, char color)
{
    int i = 0;
    while (*mode != color && *(++mode)) {
        ++i;
    }
    return i;
}

#endif