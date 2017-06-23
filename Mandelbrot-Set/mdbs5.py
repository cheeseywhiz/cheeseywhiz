# R-like dict implementation of Cython implementation of wikipedia
# implementation

import time
from cpy.mdbs2 import escape, hue
from pxaccess import PixelAccess_Int


def mdbs(xmin=-2, xmax=2, ymin=-2, ymax=2, w=1024, h=1024, break_point=100):
    def color(x, y):
        hue_ = int(hue(escape(x, y, break_point)))
        return (hue_, 255, 127) if hue_ else (0, 0, 0)

    px = PixelAccess_Int(xmin, xmax, ymin, ymax, w, h)
    px.map(color)
    px.save(f'imgs/{int(time.time())}.png', 'HSV')
