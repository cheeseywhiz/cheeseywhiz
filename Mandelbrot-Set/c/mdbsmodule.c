#include <Python.h>
#include <stdio.h>
#include "math_ops.h"

static char mdbs_doc[] = "\
Provides C implementation of escape function for Mandelbrot sets.\
";

static char mdbs_escape_doc[] = "\
escape(real: float, imag: float, limit=100: int) -> float\n\
\n\
Find how long it takes to escape past radius 2 for complex num at\n\
real + imag * i. The limit keyword argument is the maximum number of loops to\n\
take before returning 0.\n\
\n\
Returns HSV hue value for escape value.\
";
static PyObject*
mdbs_escape(PyObject *self, PyObject *args, PyObject *kwargs) {
    double real, imag;

    char *args_kwargs_list[] = {"real", "imag", "limit", NULL};
    int limit = 100;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "dd|$i", args_kwargs_list,
                                     &real, &imag, &limit)) {
        return NULL;
    };

    /* TODO: Make escape() take a Py_complex and return a PyObject* float. */
    return Py_BuildValue("d", escape(real, imag, limit));
};

static PyMethodDef mdbs_methods[] = {
    {"escape", (PyCFunction)mdbs_escape, METH_VARARGS | METH_KEYWORDS, mdbs_escape_doc},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mdbsmodule = {
    PyModuleDef_HEAD_INIT,
    "mdbs",
    mdbs_doc,
    -1,
    mdbs_methods
};

PyMODINIT_FUNC
PyInit_mdbs(void) {
    return PyModule_Create(&mdbsmodule);
};

int
main(int argc, char* argv[]) {
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    PyImport_AppendInittab("mdbs", PyInit_mdbs);
    Py_SetProgramName(program);
    Py_Initialize();
    PyImport_ImportModule("mdbs");
    PyMem_RawFree(program);

    return 0;
};
