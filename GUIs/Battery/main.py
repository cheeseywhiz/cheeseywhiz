#!/usr/bin/env python3
import graph
import sys
from PySide.QtCore import *
from PySide.QtGui import *


class DesktopWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setCentralWidget(ImageWidget())
        # TODO: scale image, set window in specific position, remove titlebar..


class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_elements()
        self.setLayout(self.image_layout())

    def init_elements(self):
        self.image = graph.LivePercentagePlot(tick=1)

    def image_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.image)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout


def main():
    app = QApplication([])
    main = DesktopWidget()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
