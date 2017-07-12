from PyQt5.QtCore import pyqtSignal, pyqtSlot, QModelIndex, QObject, QSize, Qt
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QVBoxLayout, QWidget,
)
from noconflict import classmaker
from get_password import get_password
from libwifi import Profile

debug = 1

if debug:
    from libwifi import random_data as wifi_data
else:
    from libwifi import wifi_data


class WifiTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WiFi Tool')
        self.widget = CentralWidget()
        self.setCentralWidget(self.widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.widget.profiles_widget.setCurrentIndex(QModelIndex())


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        self.widgets = self.init_sub_widgets()
        self.setLayout(self.central_layout())

    def init_sub_widgets(self):
        self.profiles_widget = ProfileTable()
        buttons = ButtonRow()
        buttons.scan_button.clicked.connect(self.scan)
        buttons.connect_button.clicked.connect(lambda: print('NotImplemented'))
        buttons.pass_button.clicked.connect(
            lambda: print(self.parse_password()))

        return (
            buttons,
            self.profiles_widget,
        )

    @pyqtSlot(QObject)
    def pf_click(self, clicked_pf):
        index = self.profiles_widget.indexFromItem(clicked_pf.item_widget)
        self.profiles_widget.setCurrentIndex(index)

    def central_layout(self):
        layout = QVBoxLayout()

        for widget in self.widgets:
            layout.addWidget(widget)

        return layout

    def scan(self):
        self.profiles_widget.clear()

        for pf in wifi_data():
            new_item = QListWidgetItem()
            new_widget = QProfile(pf, self, new_item)
            new_height = new_widget.minimumSize().height()
            new_item.setSizeHint(QSize(-1, new_height))
            self.profiles_widget.addItem(new_item)
            self.profiles_widget.setItemWidget(new_item, new_widget)

    def parse_password(self):
        while True:
            # Loop while user entry is invalid
            key = get_password()

            if key is None:
                # Do nothing if user cancelled
                return
            elif len(key) < 8:
                print('Error: password shorter than 8 characters')
            elif len(key) > 63:
                print('Error: password longer than 63 characters')
            else:
                return key


class ProfileTable(QListWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(self.ScrollPerItem)
        self.setSelectionMode(self.SingleSelection)

    def current_pf(self):
        index = self.currentIndex()
        return self.indexWidget(index)


class ButtonRow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        self.setLayout(self.layout(self.widgets()))

    def widgets(self):
        self.scan_button = QPushButton('Scan')
        self.connect_button = QPushButton('Connect')
        self.pass_button = QPushButton('Enter password')

        return [self.scan_button, self.connect_button, self.pass_button]

    def layout(self, widgets):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for button in widgets:
            layout.addWidget(button)

        return layout


class QProfile(Profile, QWidget, metaclass=classmaker()):
    clicked = pyqtSignal(QObject)

    def __init__(self, pf_dict, parent=None, item_widget=None):
        Profile.__init__(self, pf_dict)
        QWidget.__init__(self)
        self._parent = parent
        self.item_widget = item_widget

        self.clicked.connect(self._parent.pf_click)

        self.widgets = self.init_sub_widgets()
        layout = self.pf_layout()
        self.setLayout(layout)

        old_min_height = self.sizeHint().height()
        new_min_height = old_min_height * 4 / 3
        min_height_diff = new_min_height - old_min_height
        self.setMinimumSize(0, new_min_height)

        layout.setContentsMargins(min_height_diff, 0, 0, 0)
        layout.setSizeConstraint(layout.SetMinimumSize)
        layout.setAlignment(Qt.AlignVCenter)

    def init_sub_widgets(self):
        pf_name = self['SSID']

        if self['connected']:
            pf_name = f'<b>{pf_name}</b>'

        pf_name = QLabel(pf_name)
        signal = QLabel(str(self['signal']))
        # font awesome lock () or empty string
        secure = QLabel(chr(61475) if self['secure'] else str())

        return (
            (0, signal),
            (0, secure),
            (1, pf_name),
        )

    def pf_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for stretch, widget in self.widgets:
            layout.addWidget(widget, stretch=stretch)

        return layout

    def mousePressEvent(self, event):
        self.clicked.emit(self)
