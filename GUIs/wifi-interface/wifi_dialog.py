from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)
# from random_data import wifi_data
from wifi_list import wifi_data


def slot(f):
    def decorated_f(child, parent, *args, **kwargs):
        return f(parent, *args, **kwargs)
    return decorated_f


class Dialog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WiFi Tool')
        # self.setCentralWidget(QProfile(self, wifi_data()[0]))  # wgt tester
        self.show()
        self.setCentralWidget(CentralWidget(self))


class CentralWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.widgets = self.init_sub_widgets()
        self.init_connections()
        self.setLayout(self.central_layout())

    def init_sub_widgets(self):
        self.scroll_area = ProfileArea()
        self.profiles_widget = QWidget()
        self.pf_layout = ProfileAreaLayout()
        self.profiles_widget.setLayout(self.pf_layout)
        self.scroll_area.setWidget(self.profiles_widget)

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
        for i in reversed(range(self.pf_layout.count())):
            widget = self.pf_layout.itemAt(i).widget()
            self.pf_layout.removeWidget(widget)
            if widget is not None:
                widget.setParent(None)

        for i, widget in enumerate(QProfile(pf) for pf in wifi_data()):
            if i % 2:
                pass  # TODO: widget.setBackgroundRole(QPalette.Midlight)
            self.pf_layout.addWidget(widget)

        self.pf_layout.addStretch(-1)

    @slot
    def connect(self):
        pass


class ProfileArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundRole(QPalette.Base)


class ProfileAreaLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addWidget(QWidget())
        self.setContentsMargins(0, 0, 0, 0)


class ScanButton(QPushButton):
    scan_event = pyqtSignal('QObject')

    def __init__(self, parent, *QPushButton_args):
        super().__init__(*QPushButton_args)
        self.parent = parent
        self.signal = self.scan_event

    def mousePressEvent(self, event):
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
    def __init__(self, pf_dict):
        super().__init__()
        self.pf_dict = pf_dict

        self.widgets = self.init_sub_widgets()
        self.setLayout(self.pf_layout())

    def init_sub_widgets(self):
        pf_name = self.pf_dict['SSID']

        if self.pf_dict['connected']:
            pf_name = f'<b>{pf_name}</b>'

        self.pf_name = QLabel(pf_name)
        self.signal = QLabel(str(self.pf_dict['signal']))
        # font awesome lock () or empty string
        self.secure = QLabel(chr(61475) if self.pf_dict['secure'] else str())

        return {
            (0, 0): self.signal,
            (0, 1): self.secure,
            (0, 2): self.pf_name,
        }

    def pf_layout(self):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 1)

        for (row, col), widget in self.widgets.items():
            layout.addWidget(widget, row, col)

        return layout
