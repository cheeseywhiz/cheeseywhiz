#!/home/cheese/cheeseywhiz/GUIs/wifi-interface/bin/python
"""\
pyrasite-shell $(ps aux | pgrep -f "wifi_interface")
"""
import sys
from PyQt5.QtWidgets import QApplication
from wifi_dialog import Dialog
from pprint import pprint as p
p


def exp(obj, instances=True):
    def recur(obj):
        try:
            children = obj.children()
            if children == []:
                raise AttributeError
        except AttributeError:
            return obj.__class__.__name__
        else:
            def value(children):
                res = [recur(child) for child in children]
                if instances:
                    return obj, res
                else:
                    return res
            return {obj.__class__.__name__: value(children)}

    res = recur(obj)
    return res


def printable(obj):
    def new_line():
        return ('\n', *(' ' * 4 * num_braces))

    str_ = str(exp(obj, instances=False))
    new_str = []
    skip = []
    num_braces = 0

    for i, char in enumerate(str_):
        if i in skip:
            continue

        if char == ']':
            num_braces -= 1
            new_str.extend(new_line())

        if str_[i:i + 3] == ': [':
            num_braces += 1
            new_str.extend([': [', *new_line()])
            skip.extend(range(i, i + 3))
            continue
        elif str_[i:i + 2] == ', ':
            new_str.extend([',', *new_line()])
            skip.extend(range(i, i + 2))
            continue

        new_str.append(char)

    new_str.append('\n')
    return ''.join(new_str)


def write():
    with open('out.py', 'w') as f:
        f.write(printable(window))


app = QApplication([])
window = Dialog()
# print(printable(window))
# write()
window.show()
sys.exit(app.exec_())
