#!/usr/bin/env python3
import time
import warnings
import matplotlib.pyplot as plt
import battery

warnings.filterwarnings('ignore', '.*GUI is implemented.*')
warnings.filterwarnings("ignore", 'Attempting to set identical')


def loop(event, tick, max_loop=0):
    """None loop(function event, float tick, int max_loop=0)

    Call <event>() a maximum of <max_loop> times every <tick> seconds.

    Set max_size to 0 to run indefinitely."""
    if not max_loop:
        from sys import maxsize
        max_loop = maxsize
        del maxsize

    t0 = time.time()
    n = 1
    print('Beginning loop.')
    event()

    try:
        while n < max_loop:
            t1 = time.time()
            if t1 - t0 >= tick:
                t0 = t1
                n += 1
                event()
    except KeyboardInterrupt:
        print('User interrupted.')
    else:
        print('Successfully looped.')


class LiveGraph:
    def __init__(self):
        self._t_0 = time.time()
        plt.ion()
        loop(self._plot_new_percentage, 30)

    def _plot_new_percentage(self):
        x, y = int(time.time() - self._t_0), self._percentage()
        print('time=%d seconds, %.9f%s'%(x, y, '%'))
        plt.axis([0, x * 1.1, 0, 100])
        plt.scatter(x, y)
        plt.pause(30)

    @staticmethod
    def _percentage():
        return float(battery.info()['percentage'][:-1])


def main():
    LiveGraph()


if __name__ == '__main__':
    main()
