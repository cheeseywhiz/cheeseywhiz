#include <Python.h>
#include <stdio.h>

static char mdbs_doc[] = "\
Provides C implementation of escape function for Mandelbrot sets.\
";

static PyObject *
escape_impl(Py_complex complex, int limit) {
    double x = 0, y = 0, x_temp, answer;
    int n;

    for (n = 0; x * x + y * y < 2 * 2 && n < limit; n++) {
        x_temp = x;
        x = x * x - y * y + complex.real;
        y = 2 * x_temp * y + complex.imag;
    };

    if (n == limit) {
        answer = 0;
    } else {
        answer = n * 255 / 45;
    };

    return Py_BuildValue("d", answer);
};

static char mdbs_escape_doc[] = "\
escape(complex: complex, limit=100: int) -> float\n\
\n\
Find how long it takes to escape past radius 2 for complex num at the given\n\
Python complex number. The limit keyword argument is the maximum number of\n\
loops to take before returning 0.\n\
\n\
Returns HSV hue value for escape value.\
";
static PyObject*
mdbs_escape(PyObject *self, PyObject *args, PyObject *kwargs) {
    Py_complex complex;
    int limit = 100;

    char *args_kwargs_list[] = {"complex", "limit", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "D|$i", args_kwargs_list,
                                     &complex, &limit))
    {
        return NULL;
    };

    return escape_impl(complex, limit);
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
