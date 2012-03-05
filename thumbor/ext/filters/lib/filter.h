#ifndef __FILTER__H__
#define __FILTER__H__

#include <Python.h>
#include "image_utils.h"

#define FILTER_MODULE(NAME, DOC)    static PyMethodDef NAME ## _methods[] = { \
                                        {"apply", NAME ## _apply, METH_VARARGS, DOC}, \
                                        {0, 0, 0, 0} \
                                    }; \
                                    PyMODINIT_FUNC init ## NAME(void) { \
                                        Py_InitModule3(#NAME, NAME ## _methods, #NAME " native module"); \
                                    }


#endif
