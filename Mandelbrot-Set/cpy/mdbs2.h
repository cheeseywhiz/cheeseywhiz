#include <math.h>

int _escape(double real, double imag, int limit) {
    double x = 0, y = 0, x_temp;
    int n = 0;

    while (x * x + y * y < 2 * 2 && n < limit) {
        x_temp = x;
        x = x * x - y * y + real;
        y = 2 * x_temp * y + imag;
        n++;
    };

    if (n == limit) {
        return 0;
    } else {
        return n;
    };
};


double _hue(int n) {
    if (n == 0) {
        return 0;
    } else {
        return (256 / M_PI) * acos(cos((M_PI / 38) * n));
    };
};
