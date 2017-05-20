#!/usr/bin/python3
import math
from PIL import Image
import ctypes
import time


def round(x, n):  # round x to n places
    return math.floor(x * 10**n) / 10**n


def floatRange(low, high, step):  # custom for range (floats)
    i = 0
    while low + i * step < high:
        yield low + i * step
        i = i + 1


# number of times it takes the iterated function to exceed the limit at
# the given complex point
def escape(complexNum, limit, accuracy):
    z = 0
    n = 0
    while abs(z * z + complexNum) < limit and n < accuracy:
        z = z * z + complexNum
        n = n + 1
    if n == accuracy:
        return 0
    else:
        return n


def alert(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0)


def imgEscape(xmin, xmax, ymin, ymax, limit, accuracy, w, h):
    img = Image.new('HSV', (w, h))
    pixel = img.load()
    for x in range(w):
        for y in range(h):
            n = escape((x * (xmax - xmin) / w + xmin) +
                       (y * (ymin - ymax) / h + ymax) * 1j, limit, accuracy)
            if n == 0:
                pixel[x, y] = (0, 0, 0)
            else:
                color = (256 / math.pi) * \
                    math.acos(math.cos((math.pi / 38) * n))
                pixel[x, y] = (int(color), 255, 127)
    file = "imgs/%d.png" % int(time.time())
    img.convert('RGB').save(file)
    alert("Mandelbrot Set", "Graph saved to %s" % file)


def main():
    print("default=-2")
    xmin = float(input("   xmin="))
    print("\ndefault=1")
    xmax = float(input("   xmax="))
    print("\ndefault=-1.5")
    ymin = float(input("   ymin="))
    print("\ndefault=1.5")
    ymax = float(input("   ymax="))
    limit = 2
    accuracy = 100
    print("\ndefault=500")
    w = int(input("  width="))
    print("\ndefault=500")
    h = int(input(" height="))
    imgEscape(xmin, xmax, ymin, ymax, limit, accuracy, w, h)


main()
