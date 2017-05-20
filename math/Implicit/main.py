import sys
from PIL import Image
import time
from math import sin


def implicit1(x, y):
    f = x * y + sin(y * y * x) - 4
    return f


def implicit(x, y):
    try:
        return eval(sys.argv[1])
    except Exception:
        return 0


def color(n):
    c = .01
    if n**2 < c**2:
        return (0, 0, 0)
    hue = (255 * c / n)**2
    return int(hue), 255, 127


def graph_implicit(xmin, xmax, ymin, ymax, w, h):
    img = Image.new('HSV', (w, h), (255, 255, 255))
    pixel = img.load()
    for xpx in range(w):
        for ypx in range(h):
            pixel[xpx, ypx] = color(implicit(xpx * (xmax - xmin) / w + xmin,
                                             ypx * (ymin - ymax) / h + ymax))
    file = 'imgs/%d.png' % time.time()
    img.convert('RGB').save(file)


if __name__ == '__main__':
    graph_implicit(-2, 2, -2, 2, 512, 512)
