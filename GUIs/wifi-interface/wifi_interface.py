#!/home/cheese/cheeseywhiz/GUIs/wifi-interface/bin/python
import sys
from PyQt5.QtWidgets import QApplication
from wifi_dialog import Dialog


def main():
    app = QApplication([])
    Dialog()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
