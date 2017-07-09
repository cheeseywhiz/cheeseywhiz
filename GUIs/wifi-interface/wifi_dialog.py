from PyQt5.QtCore import (
    pyqtSignal, pyqtSlot, QObject, QItemSelectionModel, QSize, Qt,
)
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QVBoxLayout, QWidget,
)
from noconflict import classmaker
from libwifi import Profile

debug = 1

if debug:
    from libwifi import random_data as wifi_data
else:
    from libwifi import wifi_data


class Dialog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WiFi Tool')
        self.widget = CentralWidget(self)
        self.setCentralWidget(self.widget)


class CentralWidget(QWidget):
    def __init__(self, _parent=None):
        super().__init__()
        self._parent = _parent

        self.widgets = self.init_sub_widgets()
        self.setLayout(self.central_layout())

    def init_sub_widgets(self):
        self.profiles_widget = ProfileTable(self)

        return [
            ButtonRow(self),
            self.profiles_widget,
        ]

    def central_layout(self):
        layout = QVBoxLayout()

        for widget in self.widgets:
            layout.addWidget(widget)

        return layout

    def scan(self):
        # delete all widgets
        for i in reversed(range(self.profiles_widget.count())):
            list_item = self.profiles_widget.item(i)
            widget = self.profiles_widget.itemWidget(list_item)
            self.profiles_widget.takeItem(i)
            widget.setParent(None)

        # generate new widgets
        for pf in wifi_data():
            new_item = QListWidgetItem()
            new_widget = QProfile(pf, self, new_item)
            new_height = new_widget.minimumSize().height()
            new_item.setSizeHint(QSize(-1, new_height))
            self.profiles_widget.addItem(new_item)
            self.profiles_widget.setItemWidget(new_item, new_widget)

    def connect(self):
        print('connect')

    @pyqtSlot(QObject)
    def pf_click(self, clicked_pf):
        index = self.profiles_widget.indexFromItem(clicked_pf.item_widget)
        self.profiles_widget.setCurrentIndex(index)


class ProfileTable(QListWidget):
    def __init__(self, _parent=None):
        super().__init__()
        self._parent = _parent

        # self.model = ProfileModel(self)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerItem)
        self.setSelectionMode(self.SingleSelection)


class ProfileModel(QItemSelectionModel):
    def __init__(self, _parent):
        super().__init__()
        self._parent = _parent


class ButtonRow(QWidget):
    def __init__(self, _parent=None):
        super().__init__()
        self._parent = _parent

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scan_button = QPushButton('Scan')
        self.scan_button.clicked.connect(self._parent.scan)
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self._parent.connect)

        for button in [self.scan_button, self.connect_button]:
            self.layout.addWidget(button)


class QProfile(Profile, QWidget, metaclass=classmaker()):
    clicked = pyqtSignal(QObject)

    def __init__(self, pf_dict, _parent=None, item_widget=None):
        Profile.__init__(self, pf_dict)
        QWidget.__init__(self)
        self._parent = _parent
        self.item_widget = item_widget

        self.widgets = self.init_sub_widgets()
        self.clicked.connect(self._parent.pf_click)
        self.setLayout(self.pf_layout())
        self.setMinimumHeight(self.minimumSizeHint().height() * 4 / 3)

    def init_sub_widgets(self):
        pf_name = self['SSID']

        if self['connected']:
            pf_name = f'<b>{pf_name}</b>'

        self.pf_name = QLabel(pf_name)
        self.signal = QLabel(str(self['signal']))
        # font awesome lock () or empty string
        self.secure = QLabel(chr(61475) if self['secure'] else str())

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

        layout.setSizeConstraint(layout.SetFixedSize)
        return layout

    def mousePressEvent(self, event):
        self.clicked.emit(self)
