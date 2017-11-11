#ifndef __FILTER__H__
#define __FILTER__H__

#include <Python.h>
#include "image_utils.h"

    #if PY_MAJOR_VERSION >= 3
        #define PyInt_AsLong PyLong_AsLong
        #define PyInt_AS_LONG PyLong_AS_LONG
        #define PyInt_Check PyLong_Check
        #define PyString_Check PyBytes_Check
        #define PyString_AsString PyBytes_AsString
        #define PyString_Size PyBytes_Size
    #endif

    #if PY_MAJOR_VERSION >= 3

        #define FILTER_MODULE(NAME, DOC) \
            static PyMethodDef NAME ## _methods[] = { \
                {"apply", NAME ## _apply, METH_VARARGS, DOC}, \
                {0, 0, 0, 0} \
            }; \
            static struct PyModuleDef NAME ## _moduledef = { \
                PyModuleDef_HEAD_INIT, \
                #NAME, \
                DOC, \
                -1, \
                NAME ## _methods, \
                NULL, \
                NULL, \
                NULL, \
                NULL, \
            };\
            PyMODINIT_FUNC PyInit_ ## NAME(void) { \
               return PyModule_Create(&NAME ## _moduledef); \
            };
    #else

        #define FILTER_MODULE(NAME, DOC) \
            static PyMethodDef NAME ## _methods[] = { \
                {"apply", NAME ## _apply, METH_VARARGS, DOC}, \
                {0, 0, 0, 0} \
            }; \
            PyMODINIT_FUNC init ## NAME(void) { \
                Py_InitModule3(#NAME, NAME ## _methods, #NAME " native module"); \
            };
    #endif

#endif
