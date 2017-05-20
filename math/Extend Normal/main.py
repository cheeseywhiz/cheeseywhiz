from math import atan, cos, sin
import matplotlib.pyplot as plt

xmin, xmax = -10, 10
ymin, ymax = -8, 8
dx_ = (xmax - xmin) / 10000


def in_domain(f, x):
    try:
        f(x)
        return True  # f(x) exists; x is in domain of f
    except Exception:
        return False  # f(x) raised an error; x is not in domain of f


def offset(f, r, show=True):
    h = 1e-6
    domain = [n * dx_
              for n in range(int(xmin / dx_), int(xmax / dx_) + 1)
              if in_domain(f, n * dx_)]
    original = [(x, f(x)) for x in domain if ymin <= f(x) <= ymax]
    offset_negative = []
    offset_positive = []
    for x, y in original:
        # perpendicular to definition of derivative represented in radian
        # measure
        theta = atan(-h / (f(x + h) - f(x)))
        dx = r * cos(theta)  # radian measure to x,y translation
        dy = r * sin(theta)
        x1, y1 = x + dx, y + dy  # translate coordinates
        x2, y2 = x - dx, y - dy
        if xmin <= x1 <= xmax and ymin <= y1 <= ymax:
            offset_negative.append((x1, y1))
        if xmin <= x2 <= xmax and ymin <= y2 <= ymax:
            offset_positive.append((x2, y2))
    original = list(zip(*original))
    offset_negative = list(zip(*offset_negative))
    offset_positive = list(zip(*offset_positive))
    plt.plot([xmin, xmax], [ymin, ymax], 'w,')
    plt.plot(original[0], original[1], 'r,')
    plt.plot(offset_negative[0], offset_negative[1], 'b,')
    plt.plot(offset_positive[0], offset_positive[1], 'b,')
    if show:
        plt.show()
