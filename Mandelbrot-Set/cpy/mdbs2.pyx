cdef extern from "mdbs2.h":
    int _escape(double real, double imag, int limit)
    double _hue(int n)


cpdef int escape(double real, double imag, int limit):
    return _escape(real, imag, limit)


cpdef double hue(int n):
    return int(_hue(n))
