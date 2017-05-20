# wikipedia implementation

import math
import time
from PIL import Image


def escape(real, imag, break_point):
    x, y, n = 0, 0, 0
    while x * x + y * y < 2 * 2 and n < break_point:
        x, y, n = x * x - y * y + real, 2 * x * y + imag, n + 1
    if n == break_point:
        return 0
    else:
        return n


def color(n):
    if n == 0:
        return (0, 0, 0)
    else:
        return (int((256 / math.pi) * math.acos(math.cos((math.pi / 38) * n))),
                255,
                127)


def mdbs(xmin, xmax, ymin, ymax, w, h, break_point):
    img = Image.new('HSV', (w, h))
    pixel = img.load()
    for x, y in [(x, y) for x in range(w) for y in range(h)]:
        pixel[x, y] = color(escape(x * (xmax - xmin) / w + xmin,
                                   y * (ymin - ymax) / h + ymax,
                                   break_point))
    img.convert('RGB').save("imgs/%d.png" % int(time.time()))
