#!/usr/bin/python3
import math
import sys
import inspect
import matplotlib.pyplot as plt
import differentiable

xmin, xmax = -2, 4
ymin, ymax = -4, 4
h = 1 / 1000

dx = differentiable.equations()


def taylor(f, center, order):
    """Plot a Taylor polynomial and its parent function
    taylor(differentiable equation f, float center, int order)
    """
    coef = [f(center, i) / math.factorial(i) for i in range(order + 1)]
    domain = [n * h for n in range(int(xmin / h), int(xmax / h) + 1)
              if differentiable.in_domain(f, n * h)]
    original = list(zip(*[(x, f(x)) for x in domain if ymin <= f(x) <= ymax]))
    dec = differentiable.evaluate_coefficients
    approximation = list(zip(*[(x, dec(coef, x - center))
                               for x in domain
                               if ymin <= dec(coef, x - center) <= ymax]))

    plt.clf()
    # graph will be at least as big as the specified domain and range
    plt.plot([xmin, xmax], [ymin, ymax], 'w')
    plt.plot(original[0], original[1], 'b')
    plt.plot(approximation[0], approximation[1], 'r')
    plt.show()


if __name__ == '__main__':
    def share_element(x, y):
        for elem in x:
            if elem in y:
                return True
        return False
    help_args = ['help', '-h', '-help', '/?']
    if share_element(sys.argv, help_args) == 1 or len(sys.argv) == 1:
        print(taylor.__doc__)
        print("""'main.py f center order' executes taylor(f,center,order)
Or run 'main.py taylor(f,center,order)'\n""")
        print([pair[0]
               for pair in inspect.getmembers(dx)
               if isinstance(pair[1], type(dx.sin))])
        sys.exit()
    if len(sys.argv) == 2:
        eval(sys.argv[1])
        sys.exit()
    if len(sys.argv) > 2:
        eval('taylor(dx.' + sys.argv[1] + ',' +
             sys.argv[2] + ',' + sys.argv[3] + ')')
        sys.exit()
