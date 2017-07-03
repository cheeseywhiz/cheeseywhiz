#include <Python.h>

static PyObject *
hue_to_rgb_impl(double hue, double sat, double val) {
    double red, green, blue;
    double chroma, diff, inter;

    hue /= 60;
    chroma = val * sat;
    diff = val - chroma;
    inter = chroma * (1 - fabs(((int) hue % 2) - 1));

    switch ((int) hue) {
        case 0: {
            red   = chroma;
            green =  inter;
            blue  =      0;
        } break;
        case 1: {
            red   =  inter;
            green = chroma;
            blue  =      0;
        } break;
        case 2: {
            red   =      0;
            green = chroma;
            blue  =  inter;
        } break;
        case 3: {
            red   =      0;
            green =  inter;
            blue  = chroma;
        } break;
        case 4: {
            red   =  inter;
            green =      0;
            blue  = chroma;
        } break;
        case 5: {
            red   = chroma;
            green =      0;
            blue  =  inter;
        } break;
        default: {
            red   =  -diff;
            green =  -diff;
            blue  =  -diff;
        } break;
    };

    red += diff;
    green += diff;
    blue += diff;

    return Py_BuildValue("(ddd)", red, green, blue);
};

static char hue_to_rgb_doc[] = "\
hue_to_rgb(hsv: tuple) -> tuple\n\
\n\
Convert an HSV tuple into an RGB tuple.\n\
\n\
The HSV tuple shall have the following structure:\n\
    (\n\
        hue: float from 0 to 360,\n\
        sat: float from 0 to 1,\n\
        val: float from 0 to 1,\n\
    )\n\
\n\
While the return RGB tuple has the following structure:\n\
    (\n\
        red: float from 0 to 1,\n\
        green: float from 0 to 1,\n\
        blue: float from 0 to 1,\n\
    )\
";
static PyObject *
hue_to_rgb(PyObject *self, PyObject *args) {
    double hue, sat, val;

    if (!PyArg_ParseTuple(args, "(ddd)",
                          &hue, &sat, &val))
    {
        return NULL;
    };

    return hue_to_rgb_impl(hue, sat, val);
};

static char mdbs_doc[] = "\
Provides C implementation of escape function for Mandelbrot sets.\
";

static PyObject *
escape_impl(Py_complex complex, int limit) {
    double x = 0, y = 0, x_temp;
    int n;
    PyObject *answer;

    for (n = 0; x * x + y * y < 2 * 2 && n < limit; n++) {
        x_temp = x;
        x = x * x - y * y + complex.real;
        y = 2 * x_temp * y + complex.imag;
    };

    if (n == limit) {
        answer = Py_BuildValue("(ddd)", 0, 0, 0);
    } else {
        answer = hue_to_rgb_impl(n, 1, 0.5);
    };

    return answer;
};

static char mdbs_escape_doc[] = "\
escape(complex: complex, limit=100: int) -> tuple\n\
\n\
Find how long it takes to escape past radius 2 for complex num at the given\n\
Python complex number. The limit keyword argument is the maximum number of\n\
loops to take before returning 0.\n\
\n\
Returns an RGB tuple representation of escape amount.\
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
    {"hue_to_rgb", (PyCFunction)hue_to_rgb, METH_VARARGS, hue_to_rgb_doc},
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
