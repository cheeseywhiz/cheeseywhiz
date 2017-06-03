#!/usr/bin/env python3

from time import clock
import matplotlib.pyplot as plt
from pyautogui import position
from decorators import foreach, timer

width, height = 1366, 768
positions = []


@timer
@foreach
def plot_lines(origin, terminus):
    x0, y0 = origin[0], height - origin[1]
    x1, y1 = terminus[0], height - terminus[1]
    plt.plot([x0, x1], [y0, y1], 'k-')


def plot(map):
    plt.clf()
    plt.plot([0, width], [0, height], 'w,')
    plot_lines(map[:-1], map[1:])
    plt.show()


def loop(interval, t_max=1e6):
    print('Press Ctrl+C to quit\nLooping...')
    break_ = False
    t0 = clock()
    while not break_ and t0 < t_max:
        try:
            t1 = clock()
            if t1 - t0 >= interval:
                t0 = t1
                positions.append(position())
        except KeyboardInterrupt:
            break_ = True
    print('\nDone looping')
