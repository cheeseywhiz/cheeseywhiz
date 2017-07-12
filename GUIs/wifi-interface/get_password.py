from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget,
)


class PasswordDialog(QDialog):
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self.value = None

        self.setWindowTitle('Enter password')

        self.pass_entry = QLineEdit()
        self.pass_entry.returnPressed.connect(self.submit)

        layout = QFormLayout()

        layout.addWidget(QLabel('Enter password:'))
        layout.addWidget(self.pass_entry)
        layout.addWidget(self.button_row())

        self.setLayout(layout)

    def button_row(self):
        submit_button = QPushButton('Connect')
        submit_button.clicked.connect(self.submit)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)

        layout = QHBoxLayout()
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


def get_password():
    return PasswordDialog().show_collect()
