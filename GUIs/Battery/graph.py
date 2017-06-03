import time
import os
import warnings
import matplotlib.pyplot as plt
import battery
try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except ModuleNotFoundError:  # no PySide
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *

# String formatting on print(time, percentage)
warnings.filterwarnings("ignore", 'Attempting to set identical')


class LivePercentagePlot(QLabel):
    """QLabel showing a plot image of battery percentage.

    kwargs:
    float <tick>:   How often to plot percentage point. Default 30.
    int <width>:    Width of graph in terms of time intervals.
                    Default 50."""
    def __init__(self, tick=30, width=50):
        """Store variables passed to the instance."""
        super().__init__()
        self.__tick = tick
        self.__width = width

        self.__image_pipe = 'graph.png'
        self.__t_0 = time.time()
        self.__x_list = []
        self.__y_list = []
        self.__style_list = []

        func = self.__plot_new_percentage
        self.__loop = QTimer()
        self.__loop.timeout.connect(func)
        func()
        self.__loop.start(self.__tick * 1000)

    def __plot_new_percentage(self):
        info = battery.info()
        percentage = float(info['percentage'][:-1])
        x, y = int(time.time() - self.__t_0), percentage
        cond = info['state'] == 'discharging'
        style = 'r.-' if cond else 'b.-'  # TODO: proper multicolored line plot
        self.__x_list.append(x)
        self.__y_list.append(y)
        self.__style_list.append(style)
        print('time=%d seconds, %.9f%s'%(x, y, '%'))
        max = self.__tick * self.__width
        offset = x - max if x > max else 0
        plt.clf()
        # plt.axis([offset, max + offset, 0, 100])
        plt.xlim(offset, max + offset)
        plt.plot(
            *self.flatten(self.__x_list,
                          self.__y_list,
                          self.__style_list)
        )
        self.__save(self.__image_pipe)

    def __save(self, file_name):
        fig = plt.gcf()
        axes = fig.gca()
        axes.set_frame_on(False)
        axes.set_xticks([])
        axes.set_yticks([])
        plt.axis('off')
        fig.savefig(file_name, bbox_inches='tight', pad_inches=0)

        file_name = os.path.abspath('graph.png')
        image = QImage(file_name)
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)

    def flatten(self, *args):
        return sum([list(item) for item in zip(*args)], [])
