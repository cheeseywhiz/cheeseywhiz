from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QPushButton
from pyqtbindings import (
    QCheckBox, QDialog, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget
)


class PasswordDialog(QDialog):
    submitted = pyqtSignal(str)
    value = None

    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)

        self.window_title = 'Enter password'

        layout = QVBoxLayout()
        layout += QLabel('Enter password:')
        layout += self.entry_row()
        layout += self.button_row()

        self.layout = layout

    def entry_row(self):
        self.pass_entry = PasswordEdit()
        self.pass_entry.returnPressed.connect(self.submit)

        check_box = QCheckBox()
        check_box.checked.connect(self.pass_entry.set_password)
        check_box.unchecked.connect(self.pass_entry.set_normal)
        check_box.check_state = Qt.Checked

        layout = QHBoxLayout()
        layout.contents_margins = 0, 0, 0, 0
        layout += self.pass_entry
        layout += check_box

        widget = QWidget()
        widget.layout = layout
        return widget

    def button_row(self):
        submit_button = QPushButton('Connect')
        submit_button.clicked.connect(self.submit)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)

        layout = QHBoxLayout()
        layout.contents_margins = 0, 0, 0, 0
        layout += submit_button
        layout += cancel_button

        widget = QWidget()
        widget.layout = layout
        return widget

    @pyqtSlot()
    def submit(self):
        self.value = self.pass_entry.text()
        self.submitted.emit(self.value)
        self.close()

    @staticmethod
    def get_password():
        self = PasswordDialog()
        self.exec_()
        return self.value


class PasswordEdit(QLineEdit):
    @pyqtSlot()
    def set_normal(self):
        self.font = QFont('Monospace')
        self.echo_mode = self.Normal

    @pyqtSlot()
    def set_password(self):
        self.font = self.default_font
        self.echo_mode = self.Password
