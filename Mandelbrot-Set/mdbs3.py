#!/usr/bin/env python3

from time import asctime
import numpy as np
import matplotlib.pyplot as plot
from decorators import timer, np_vector

xmin, xmax = -683 / 192, 683 / 192
ymin, ymax = -2, 2
width, height = 1366 * 2, 768 * 2


@timer
@np_vector
def mdbs_vector(c, limit):
    z = 0
    n = 0
    for i in range(limit):
        if np.abs(z) < 2:
            n += 1
        else:
            break
        z = z * z + c
    return np.log1p(1 / n)


x, y = np.meshgrid(np.linspace(xmin, xmax, width),
                   np.linspace(ymin, ymax, height))

plot.imsave('/home/cheeseywhiz/Desktop/%s'%asctime(),
            mdbs_vector(x + y * 1j, 100),
            cmap='nipy_spectral')
