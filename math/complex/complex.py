import cmath
import numpy as np
# from matplotlib import pyplot as plt
import tint


def func(c):
    return cmath.sqrt(c - 1)


def white_blank(shape):
    array = np.empty(shape, np.uint8)

    for i, row in enumerate(array):
        for j, pixel in enumerate(row):
            array[i, j] = 255

    return array


class GrayImagePath(tint.ImagePath):
    xmax = 2
    xmin = -xmax

    def transform(self, func):
        array = self.array
        new_array = white_blank(array.shape[:2])
        xy, pos = conversions(self.xmin, self.xmax, array.shape)
        visited = set()

        for i, row in enumerate(array):
            for j, pixel in enumerate(row):
                if (i, j) in visited:
                    continue

                real, imag = xy(i, j)
                new_pos = pos(func(real + imag * 1j))

                if new_pos in visited:
                    continue

                try:
                    new_array[new_pos] = pixel
                except IndexError:
                    continue

                visited.add(new_pos)

        return new_array


def conversions(xmin, xmax, shape):
    height, width = shape
    ymax = (xmax - xmin) * width / height
    ymin = -ymax

    def pos_to_xy(i, j):
        x = i * (xmax - xmin) / width + xmin
        y = j * (ymin - ymax) / height + ymax
        return x, y

    def xy_to_pos(c):
        x, y = c.real, c.imag
        i = width * (x - xmin) / (xmax - xmin)
        j = height * (y - ymax) / (ymin - ymax)
        return tuple(map(int, (i, j)))

    return pos_to_xy, xy_to_pos
