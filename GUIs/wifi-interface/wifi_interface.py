#!/home/cheese/cheeseywhiz/GUIs/wifi-interface/bin/python
"""\
pyrasite-shell $(ps aux | pgrep -f "wifi_interface")
"""
import sys
from PyQt5.QtWidgets import QApplication
from wifi_dialog import WifiTool

if __name__ == '__main__':
    app = QApplication([])
    window = WifiTool()
    window.show()
    sys.exit(app.exec_())
