# Cython implementation of wikipedia implementation

import time
from PIL import Image
from cpy.mdbs import escape, hue


def mdbs(xmin, xmax, ymin, ymax, w, h, break_point):
    img = Image.new('HSV', (w, h))
    pixel = img.load()
    for x, y in [(x, y) for x in range(w) for y in range(h)]:
        hue_ = int(hue(
            escape(
                x * (xmax - xmin) / w + xmin,
                y * (ymin - ymax) / h + ymax,
                break_point)
        ))
        pixel[x, y] = (hue_, 255, 127) if hue_ else (0, 0, 0)
    img.convert('RGB').save(f'imgs/{int(time.time())}.png')
