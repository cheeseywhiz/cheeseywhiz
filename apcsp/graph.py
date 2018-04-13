#!/bin/env python3
"""
Graph a family of level surfaces for a function of three variables.

Example function:
f(x, y, z) = (z ** 2) / (x ** 2 + y ** 2)
"""
import sys
import numpy as np
import sympy
import matplotlib
matplotlib.use('Qt5Cairo')

from matplotlib import cm

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

x, y, z, C = sympy.symbols('x,y,z,C', real=True)


def prompt():
    """Gather a mathematical expression from the user. Raises OSError on
    data/flag mismatch.

    $ ./graph.py  # Interactive prompt
    z=f(x, y)=sin(x+y)

    $ ./graph.py "sin(x+y)"  # Pass expression as parameter

    $ echo "sin(x+y)" | ./graph.py -  # Pass expression over pipe
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == '-':
            if sys.stdin.isatty():
                raise OSError('\'-\' flag with no data')
            else:
                return sys.stdin.read()
        else:
            return sys.argv[1]
    elif sys.stdin.isatty():
        return input('f(x, y, z)=')
    else:
        raise OSError('data with no \'-\' flag')


def get_expr_C():
    expr_xyz = eval(prompt(), vars(sympy), {'x': x, 'y': y, 'z': z})
    return sympy.solve(sympy.Eq(C, expr_xyz), z)


def main():
    fig = plt.figure()
    ax = Axes3D(fig)

    x_d = np.arange(-10, 10)
    y_d = np.arange(-10, 10)
    x_d, y_d = np.meshgrid(x_d, y_d)
    exprs = get_expr_C()
    print(exprs[-1])
    constants = list(range(200, -200 - 1, -50))

    for n, constant in enumerate(constants):
        color = cm.jet(n / (len(constants) - 1), 0.93)

        for expr in exprs:
            z_r = np.zeros(x_d.shape)
            f_xy = sympy.Lambda((x, y), expr.subs(C, constant))

            for i in range(x_d.shape[0]):
                for j in range(x_d.shape[1]):
                    ans = f_xy(x_d[i][j], y_d[i][j])
                    z_r[i][j] = ans if ans.is_real else np.nan

            # mlab.surf(x_d, y_d, z_r, color=color)
            ax.plot_surface(x_d, y_d, z_r, color=color, antialiased=False)

    # mlab.show()
    plt.show()


if __name__ == '__main__':
    main()
