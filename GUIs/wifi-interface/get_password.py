from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)


class PasswordDialog(QDialog):
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self.value = None

        self.setWindowTitle('Enter password')

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Enter password:'))
        layout.addWidget(self.entry_row())
        layout.addWidget(self.button_row())

        self.setLayout(layout)

    def entry_row(self):
        self.pass_entry = PasswordEdit()
        self.pass_entry.returnPressed.connect(self.submit)

        check_box = SmartCheckBox()  # ('Hide')
        check_box.checked.connect(self.pass_entry.set_password)
        check_box.unchecked.connect(self.pass_entry.set_normal)
        check_box.setCheckState(Qt.Checked)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pass_entry)
        layout.addWidget(check_box)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def button_row(self):
        submit_button = QPushButton('Connect')
        submit_button.clicked.connect(self.submit)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(submit_button)
        layout.addWidget(cancel_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def submit(self):
        self.value = self.pass_entry.text()
        self.submitted.emit(self.value)
        self.close()

    def show_collect(self):
        self.exec_()
        return self.value


class PasswordEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.default_font = self.font()

    def set_normal(self):
        self.setFont(QFont('Monospace'))
        self.setEchoMode(self.Normal)

    def set_password(self):
        self.setFont(self.default_font)
        self.setEchoMode(self.Password)


class SmartCheckBox(QCheckBox):
    checked = pyqtSignal()
    unchecked = pyqtSignal()

    def __init__(self, *QCheckBox_args):
        super().__init__(*QCheckBox_args)
        self.stateChanged.connect(self.handle_state_change)

    def handle_state_change(self, state):
        if state == Qt.Checked:
            self.checked.emit()
        elif state == Qt.Unchecked:
            self.unchecked.emit()


def get_password():
    return PasswordDialog().show_collect()
