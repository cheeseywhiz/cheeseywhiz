from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)
from random_data import wifi_data
# from wifi_list import wifi_data


class Dialog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WiFi Tool')
        self.widget = CentralWidget(self)
        self.setCentralWidget(self.widget)


class CentralWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.previous_pf = None

        self.widgets = self.init_sub_widgets()
        self.init_connections()
        self.setLayout(self.central_layout())

    def init_sub_widgets(self):
        self.scroll_area = ProfileArea()
        self.profiles_widget = QWidget()
        self.pf_layout = QVBoxLayout()
        self.pf_layout.setContentsMargins(0, 0, 0, 0)
        self.pf_layout.setSpacing(0)
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
        self.scan_button = QPushButton('Scan')
        self.connect_button = QPushButton('Connect')

        for button in [self.scan_button, self.connect_button]:
            layout.addWidget(button)

        widget.setLayout(layout)
        return widget

    def init_connections(self):
        self.scan_button.clicked.connect(self.scan)
        self.connect_button.clicked.connect(self.connect)

    def central_layout(self):
        layout = QVBoxLayout()

        for widget in self.widgets:
            layout.addWidget(widget)

        return layout

    def scan(self):
        for i in reversed(range(self.pf_layout.count())):
            widget = self.pf_layout.itemAt(i).widget()
            self.pf_layout.removeWidget(widget)
            if widget is not None:
                widget.setParent(None)

        for i, widget in enumerate(QProfile(pf) for pf in wifi_data()):
            if i % 2:
                widget.default_role = QPalette.Midlight
            else:
                widget.default_role = QPalette.Base
            widget.clicked.connect(self.pf_click)
            self.pf_layout.addWidget(widget)

        self.pf_layout.addStretch(-1)

    def connect(self):
        print('connect')

    @pyqtSlot(QObject)
    def pf_click(self, clicked_pf):
        if self.previous_pf is not None:
            self.previous_pf.setBackgroundRole(self.previous_pf.default_role)
        clicked_pf.setBackgroundRole(QPalette.Highlight)
        self.previous_pf = clicked_pf


class ProfileArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundRole(QPalette.Base)


class QProfile(QWidget):
    clicked = pyqtSignal(QObject)

    def __init__(self, Pf_inst):
        super().__init__()
        self.Pf_inst = Pf_inst
        self._default_role = None

        self.setAutoFillBackground(True)
        self.widgets = self.init_sub_widgets()
        self.setLayout(self.pf_layout())

    def init_sub_widgets(self):
        pf_name = self.Pf_inst['SSID']

        if self.Pf_inst['connected']:
            pf_name = f'<b>{pf_name}</b>'

        self.pf_name = QLabel(pf_name)
        self.signal = QLabel(str(self.Pf_inst['signal']))
        # font awesome lock () or empty string
        self.secure = QLabel(chr(61475) if self.Pf_inst['secure'] else str())

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

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        self.setBackgroundRole(QPalette.Highlight)

    @property
    def default_role(self):
        return self._default_role

    @default_role.setter
    def default_role(self, role):
        self._default_role = role
        self.setBackgroundRole(role)
