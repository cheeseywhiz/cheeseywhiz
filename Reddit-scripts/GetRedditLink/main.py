#!/usr/bin/python3
import sys
from PyQt5 import QtWidgets
from Dialogs import Input


def main():
    app = QtWidgets.QApplication([])
    Input.InputDialog()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
