import time
import os  # temp: for opening file in browser
from urllib.request import pathname2url  # temp
import warnings
import webbrowser  # temp
import matplotlib.pyplot as plt
import battery

# matplotlib.pyplot event loop warning
warnings.filterwarnings('ignore', '.*GUI is implemented.*')
# String formatting on print(time, percentage)
warnings.filterwarnings("ignore", 'Attempting to set identical')


def save(file_name, fig=plt.gcf()):
    """Save a Matplotlib figure as an image without borders or frames.

    args:
    str <file_name>: String that ends in .png etc.

    kwargs:
    matplotlib.figure.Figure <fig>: figure you want to save as the
                                    image. Default matplotlib.pyplot.gcf()."""
    axes = fig.gca()
    axes.set_frame_on(False)
    axes.set_xticks([])
    axes.set_yticks([])
    plt.axis('off')
    fig.savefig(file_name, bbox_inches='tight', pad_inches=0)


class Loop:
    """Call a function after an amount of time on repeat.

    args:
    function <event>: A callable object that is called on each loop.
    float <tick>:     Interval of time between each loop.

    kwargs:
    int <max_loop>: Maximum number of loops to complete. Set to 0 to run
                    forever. Default 0."""
    def __init__(self, event, tick, max_loop=0):
        """Initiate variables required for the Loop."""
        self.__event = event
        self.__tick = tick
        if not max_loop:
            from sys import maxsize
            self.__max_loop = maxsize
            del maxsize
        else:
            self.__max_loop = max_loop

    def start(self):
        """Commence the Loop."""
        n = 0
        t0 = time.time()
        try:
            while n < self.__max_loop:
                t1 = time.time()
                if t1 - t0 >= self.__tick:
                    t0 = t1
                    n += 1
                    self.__event()
        except KeyboardInterrupt as error:
            print(error)

    def kill(self):
        """Terminate the Loop after having started it."""
        raise KeyboardInterrupt('User interrupted')


class PlotLivePercentage:
    """Plot live battery percentage.

    kwargs:
    float <tick>:   How often to plot percentage point. Default 30.
    int <max_loop>: How many points to plot. Set to 0 to loop forever.
                    Default 0.
    int <width>:    Number of points at most to fit on the scrolling graph.
                    Default 50."""
    def __init__(self, tick=30, max_loop=0, width=50):
        """Initiate variables required for the Live Percentage Plot."""
        self.__tick = tick
        self.__width = width
        self.__max_loop = max_loop
        self.__t_0 = time.time()
        self.__x_list = []
        self.__y_list = []

    def start(self):
        """Commence plotting percentage points."""
        self.__loop = Loop(
            self.__plot_new_percentage,
            self.__tick,
            self.__max_loop)
        self.__loop.start()

    def __plot_new_percentage(self):
        x, y = int(time.time() - self.__t_0), self.__percentage()
        self.__x_list.append(x)
        self.__y_list.append(y)
        print('time=%d seconds, %.9f%s'%(x, y, '%'))
        max = self.__tick * self.__width
        offset = x - max if x > max else 0
        plt.clf()
        plt.axis([self.__tick + offset, max + offset, 0, 100])
        plt.plot(self.__x_list, self.__y_list, 'b.-')
        save('graph.png')
        # TODO: send Qt signal
        #
        # temp
        webbrowser.open('file:%s'%pathname2url(os.path.abspath('graph.png')))

    def __percentage(self):
        return float(battery.info()['percentage'][:-1])
