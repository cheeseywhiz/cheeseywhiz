import time
import warnings
import matplotlib.pyplot as plt
import battery

# matplotlib.pyplot event loop warning
warnings.filterwarnings('ignore', '.*GUI is implemented.*')
# String formatting on print(time, percentage)
warnings.filterwarnings("ignore", 'Attempting to set identical')


def loop(event, tick, max_loop=0):
    """None loop(function event, float tick, int max_loop=0)

    Call <event>() a maximum of <max_loop> times every <tick> seconds.

    Set max_size to 0 to run indefinitely."""
    if not max_loop:
        from sys import maxsize
        max_loop = maxsize
        del maxsize

    n = 1
    t0 = time.time()
    print('Beginning loop.')

    try:
        while n < max_loop:
            t1 = time.time()
            elapsed = t1 - t0
            if elapsed >= tick:
                t0 = t1
                n += 1
                event()
    except KeyboardInterrupt:
        print('User interrupted.')
    else:
        print('Successfully looped.')


class LiveGraph:
    """Plot live percentage data

    Call loop() on an instance to begin plotting."""
    def __init__(self):
        plt.ion()

    def __plot_new_percentage(self):
        x, y = int(time.time() - self.__t_0), self.__percentage()
        print('time=%d seconds, %.9f%s'%(x, y, '%'))
        plt.axis([0, x * 1.1, 0, 100])
        plt.scatter(x, y)
        plt.pause(self.__tick - 1)

    def loop(self, tick=30, max_loop=0):
        """None loop(float tick=30, int max_loop=0)

        Begin looping battery percentage graph.
        Check for a new percentage every <tick> seconds and plot a maximum of
        <max_loop> points. Set max_loop to 0 to loop forever."""
        self.__tick = tick
        self.__t_0 = time.time()
        loop(self.__plot_new_percentage, tick, max_loop)

    @staticmethod
    def __percentage():
        return float(battery.info()['percentage'][:-1])
