from PyQt5.QtCore import pyqtSignal, pyqtSlot, QModelIndex, QObject, QSize, Qt
from PyQt5.QtWidgets import QLabel, QPushButton
from pyqtbindings import (
    QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow, QVBoxLayout,
    QWidget,
)
from get_password import PasswordDialog
from libwifi import Profile

debug = not __debug__

if debug:
    from libwifi import random_data as wifi_data
else:
    from libwifi import wifi_data


class WifiTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_title = 'WiFi Tool'
        self.central_widget = CentralWidget()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.central_widget.profiles_widget.current_index = QModelIndex()


class CentralWidget(QWidget):
    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.widgets = self.init_sub_widgets()
        self.layout = self.central_layout()

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

    def central_layout(self):
        layout = QVBoxLayout()

        for widget in self.widgets:
            layout += widget

        return layout

    @pyqtSlot(QObject)
    def pf_click(self, clicked_pf):
        index = self.profiles_widget.indexFromItem(clicked_pf.item_widget)
        self.profiles_widget.current_index = index

    @pyqtSlot()
    def scan(self):
        self.profiles_widget.clear()

        for pf in wifi_data():
            new_item = QListWidgetItem()
            new_widget = QProfile(pf, item_widget=new_item)
            new_widget.clicked.connect(self.pf_click)
            new_height = new_widget.minimum_size.height()
            new_item.size_hint = QSize(-1, new_height)
            self.profiles_widget.addItem(new_item)
            self.profiles_widget.setItemWidget(new_item, new_widget)

    def parse_password(self):
        while True:
            # Loop while user entry is invalid
            key = PasswordDialog.get_password()

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
    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.alternating_row_colors = True
        self.horizontal_scroll_bar_policy = Qt.ScrollBarAlwaysOff
        self.vertical_scroll_mode = self.ScrollPerItem
        self.selection_mode = self.SingleSelection

    @property
    def current_pf(self):
        return self[self.current_index]


class ButtonRow(QWidget):
    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.layout = self.default_layout(self.widgets())

    def widgets(self):
        self.scan_button = QPushButton('Scan')
        self.connect_button = QPushButton('Connect')
        self.pass_button = QPushButton('Enter password')

        return (self.scan_button, self.connect_button, self.pass_button)

    def default_layout(self, widgets):
        layout = QHBoxLayout()
        layout.contents_margins = 0, 0, 0, 0

        for button in widgets:
            layout += button

        return layout


class QProfile(QWidget):
    clicked = pyqtSignal(QObject)

    def __init__(self, pf_dict, *base_args, item_widget=None, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.pf = Profile(pf_dict)
        self.item_widget = item_widget

        self.widgets = self.init_sub_widgets()
        layout = self.pf_layout()
        self.layout = layout

        old_min_height = self.size_hint.height()
        new_min_height = old_min_height * 4 / 3
        min_height_diff = new_min_height - old_min_height
        self.minimum_size = 0, new_min_height

        layout.contents_margins = min_height_diff, 0, 0, 0
        layout.size_constraint = layout.SetMinimumSize
        layout.alignment_ = Qt.AlignVCenter

    def init_sub_widgets(self):
        pf_name = self.pf['SSID']

        if self.pf['connected']:
            pf_name = f'<b>{pf_name}</b>'

        pf_name = QLabel(pf_name)
        signal = QLabel(str(self.pf['signal']))
        # font awesome lock ()
        secure = QLabel(chr(61475) if self.pf['secure'] else '')

        return (
            (0, signal),
            (0, secure),
            (1, pf_name),
        )

    def pf_layout(self):
        layout = QHBoxLayout()
        layout.contents_margins = 0, 0, 0, 0

        for stretch, widget in self.widgets:
            layout.addWidget(widget, stretch=stretch)

        return layout

    def mousePressEvent(self, event):
        self.clicked.emit(self)
