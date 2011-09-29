#ifndef __FILTER__H__
#define __FILTER__H__

#include <Python.h>

#define ADJUST_COLOR(c) ((c > 255) ? 255 : ((c < 0) ? 0 : c))

#define FILTER_MODULE(NAME, DOC) static PyMethodDef NAME ## _methods[] = { \
                                {"apply", NAME ## _apply, METH_VARARGS, DOC}, \
                                {NULL, NULL} \
                            }; \
                            PyMODINIT_FUNC init ## NAME(void) { \
                                Py_InitModule3(#NAME, NAME ## _methods, #NAME " native module"); \
                            }

#endif