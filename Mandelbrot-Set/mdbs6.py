import time
from math import fabs
import numpy as np
import matplotlib.pyplot as plt
from c import escape


def _hue_to_rgb(hue):
    if hue == 0:
        return 0, 0, 0
    else:
        hue, sat, val = hue, 255 / 255, 127 / 255
        chroma = val * sat
        hue_prime = hue / 60
        inter = chroma * (1 - fabs((hue_prime % 2) - 1))

        if 0 <= hue_prime <= 1:
            red, green, blue = chroma, inter, 0
        elif 1 < hue_prime <= 2:
            red, green, blue = inter, chroma, 0
        elif 2 < hue_prime <= 3:
            red, green, blue = 0, chroma, inter
        elif 3 < hue_prime <= 4:
            red, green, blue = 0, inter, chroma
        elif 4 < hue_prime <= 5:
            red, green, blue = inter, 0, chroma
        elif 5 < hue_prime <= 6:
            red, green, blue = chroma, 0, inter

        m = val - chroma
        red, green, blue = red + m, green + m, blue + m
        return red * 256, green * 256, blue * 256


def mdbs(xmin=-2, xmax=2, ymin=-2, ymax=2, width=1024, height=1024, limit=100):
    x = np.linspace(xmin, xmax, num=width)
    y = np.linspace(ymin, ymax, num=height)
    x, y = np.meshgrid(x, y)
    z = x + y * 1j

    def make_color(complex):
        return escape(complex, limit=limit)

    image = np.vectorize(make_color)(z)
    plt.imsave(f'{int(time())}.png', image, cmap=plt.get_cmap('Wistia_r'))
