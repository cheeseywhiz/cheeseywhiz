#!/bin/env python3
"""Graph a family of level surfaces for a function of three variables.

Example function:
f(x,y,z)=(z**2)/(x**2+y**2)"""
import sys
import numpy as np
import sympy
import matplotlib
matplotlib.use('Qt5Agg')

from sympy.abc import x, y, z, C
from matplotlib import cm
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def repeat(obj):
    while True:
        yield obj


def prompt_expr():
    """Gather a mathematical expression from the user. Raises OSError on
    data/pipe mismatch.

    $ ./graph.py  # Interactive prompt
    f(x,y,z)=(z**2)/(x**2+y**2)

    $ ./graph.py "(z**2)/(x**2+y**2)"  # Pass expression as parameter

    $ echo "(z**2)/(x**2+y**2)" | ./graph.py -  # Pass expression over pipe"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '-':
            if sys.stdin.isatty():
                raise OSError('\'-\' flag with no pipe')
            else:
                return sys.stdin.read()
        else:
            return sys.argv[1]
    elif sys.stdin.isatty():
        return input('f(x,y,z)=')
    else:
        raise OSError('pipe with no \'-\' flag')


def eval_str(str_expr):
    """Evaluate a string expression into a sympy expression. Available
    namespace is that of sympy.* and x, y, and z variables."""
    return eval(str_expr, vars(sympy), {'x': x, 'y': y, 'z': z})


def solve_z(sympy_expr):
    """Solve C=f(x,y,z) for z for some sympy expression f(x,y,z). Returns a
    list of expressions with variables x, y, and C."""
    return sympy.solve(sympy.Eq(C, sympy_expr), z)


def solve_z_str(str_expr):
    """Solve C=f(x,y,z) for z for some string expression f(x,y,z)."""
    return solve_z(eval_str(str_expr))


def solve_z_prompt():
    """Solve C=f(x,y,z) for z for some expression f(x,y,z) that is prompted
    for to the user."""
    return solve_z_str(prompt_expr())


def expr_to_f_xy(sympy_expr, constant):
    """Form a function of two variables from the sympy expression while
    substituting the arbitrary constant C."""
    return sympy.Lambda((x, y), sympy_expr.subs(C, constant))


# named after enumerate but for colors
def e_color_ate(constants):
    """Generate corresponding colors for each constant. Yields
    color, constant."""
    d = len(constants) - 1

    for n, constant in enumerate(constants):
        color = cm.jet(n / d, 0.93)
        yield color, constant


def map_f_xy(f, x_domain, y_domain):
    """Map meshgrid matrices to a function of two variables."""
    z_range = np.empty(x_domain.shape)

    for i in range(x_domain.shape[0]):
        for j in range(x_domain.shape[1]):
            ans = f(x_domain[i][j], y_domain[i][j])
            z_range[i][j] = ans if ans.is_real else np.nan

    return z_range


class LevelSurfacePlotter(Axes3D):
    """Plot functions of two variables or level curves of functions of three
    variables."""

    def plot_map_f_xy(self, f, x, y, **kwargs):
        """Plot f(x,y) in three dimensions."""
        z = map_f_xy(f, x, y)
        super().plot_surface(x, y, z, **kwargs)

    def plot_map_f_xyz(self, sympy_expr, x, y, C_list, **kwargs):
        """Plot f(x,y,z) set equal to various constants and solved for
        z=g(x,y)."""
        for color, constant in e_color_ate(C_list):
            for f_xy in map(expr_to_f_xy, sympy_expr, repeat(constant)):
                self.plot_map_f_xy(f_xy, x, y, color=color, **kwargs)


def main():
    fig = plt.figure()
    ax = LevelSurfacePlotter(fig)

    x_d = np.arange(-10, 10)
    y_d = np.arange(-10, 10)
    x_d, y_d = np.meshgrid(x_d, y_d)

    ax.plot_map_f_xyz(solve_z_prompt(), x_d, y_d, range(200, -200 - 1, -50))
    plt.show()


if __name__ == '__main__':
    main()
