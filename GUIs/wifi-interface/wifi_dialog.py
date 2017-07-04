from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)
from PyQt5.QtCore import pyqtSignal, QObject
from random_data import wifi_data
# from wifi_data import wifi_data


def slot(f):
    def decorated_f(emitter, parent, *args, **kwargs):
        return f(parent, *args, **kwargs)
    return decorated_f


class Dialog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WiFi Tool')
        # self.setCentralWidget(QProfile(self, wifi_data()[0]))  # wgt tester
        self.setCentralWidget(CentralWidget(self))
        self.show()


class CentralWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.widgets = self.init_sub_widgets()
        self.init_connections()
        self.setLayout(self.central_layout())

    def init_sub_widgets(self):
        self.scroll_area = ProfileArea()
        self.profile_scroll = QWidget()
        self.profile_layout = QVBoxLayout()
        self.profile_scroll.setLayout(self.profile_layout)
        self.scroll_area.setWidget(self.profile_scroll)

        return [
            self.button_row(),
            self.scroll_area,
        ]

    def button_row(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scan_button = ScanButton(self, 'Scan')
        self.connect_button = ConnectButton(self, 'Connect')

        for button in [self.scan_button, self.connect_button]:
            layout.addWidget(button)

        widget.setLayout(layout)
        return widget

    def init_connections(self):
        self.scan_button.signal.connect(self.scan)
        self.connect_button.signal.connect(self.connect)

    def central_layout(self):
        layout = QVBoxLayout()

        for widget in self.widgets:
            layout.addWidget(widget)

        return layout

    @slot
    def scan(self):
        print('\'Scan\' pressed')

        for i in reversed(range(self.profile_layout.count())):
            self.profile_layout.itemAt(i).widget().setParent(None)

        for widget in (QProfile(self, pf) for pf in wifi_data()):
            self.profile_layout.addWidget(widget)

    @slot
    def connect(self):
        pass


class ProfileArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)


class ScanButton(QPushButton):
    scan_event = pyqtSignal('QObject')

    def __init__(self, parent, *QPushButton_args):
        super().__init__(*QPushButton_args)
        self.parent = parent
        self.signal = self.scan_event

    def keyPressEvent(self, event):
        self.scan_event.emit(self.parent)


class ConnectButton(QPushButton):
    connect_event = pyqtSignal('QObject')

    def __init__(self, parent, *QPushButton_args):
        super().__init__(*QPushButton_args)
        self.parent = parent
        self.signal = self.connect_event

    def keyPressEvent(self, event):
        self.connect_event.emit(self.parent)


class QProfile(QWidget):
    def __init__(self, parent, profile_dict):
        super().__init__()
        self.parent = parent
        self.pf_dict = profile_dict

        self.widgets = self.init_sub_widgets()
        self.setLayout(self.profile_layout())

    def init_sub_widgets(self):
        pf_name = self.pf_dict['SSID']

        if self.pf_dict['connected']:
            pf_name = f'<b>{pf_name}</b>'

        self.pf_name = QLabel(pf_name)
        self.signal = QLabel(str(self.pf_dict['signal']))
        # font awesome lock or empty string
        self.secure = QLabel(chr(61475) if self.pf_dict['secure'] else str())

        return {
            (0, 0): self.signal,
            (0, 1): self.secure,
            (0, 2): self.pf_name,
        }

    def profile_layout(self):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 1)

        for (row, col), widget in self.widgets.items():
            layout.addWidget(widget, row, col)

        return layout


def confuse_anaconda():
    # Used in pyqtSignal
    QObject
