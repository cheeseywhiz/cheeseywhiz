cpdef double escape(double real, double imag, int limit):
    cdef double x, x_temp, y
    cdef int n
    x = 0
    y = 0
    n = 0
    
    while x ** 2 + y ** 2 < 2 ** 2 and n < limit:
        x_temp = x
        x = x ** 2  - y ** 2 + real
        y = 2 * x_temp * y + imag
        n = n + 1

    if n == limit:
        return 0
    else:
        return n


cdef extern from "math.h":
    double cos(double x)
    double acos(double x)
    double M_PI

cpdef double hue(int n):
    if n == 0:
        return 0
    else:
        return (256 / M_PI) * acos(cos((M_PI / 38) * n))
