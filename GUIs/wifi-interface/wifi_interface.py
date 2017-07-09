#!/home/cheese/cheeseywhiz/GUIs/wifi-interface/bin/python
"""\
pyrasite-shell $(ps aux | pgrep -f "wifi_interface")
"""
import sys
from PyQt5.QtWidgets import QApplication
from wifi_dialog import Dialog
from pprint import pprint as p
p


def exp(obj, printable=False):
    def repr_(obj):
        if printable:
            return repr(obj)
        else:
            return obj

    def recur(obj, parent=None):
        def instance_name(obj, parent):
            if parent is not None and hasattr(parent, '__dict__'):
                for name, attr in parent.__dict__.items():
                    if obj is attr:
                        return name
                else:
                    return obj.__class__.__name__

            return obj.__class__.__name__

        try:
            children = obj.children()

            if children == []:
                raise AttributeError

        except AttributeError:
            return repr_(obj), instance_name(obj, parent)

        else:
            return {instance_name(obj, parent): (repr_(obj), [
                    recur(child)
                    for child in children])}

    try:
        parent = obj.parent()
        if parent is None:
            raise AttributeError
    except AttributeError:
        parent = type('Globals', (object, ), globals())

    res = recur(obj, parent=parent)
    return res


def printable(obj):
    def new_line():
        return ('\n', *(' ' * 4 * num_braces))

    str_ = str(exp(obj, printable=True))
    new_str = []
    skip = []
    num_braces = 0
    in_tuple = 0

    for i, char in enumerate(str_):
        if i in skip:
            continue

        if char == '[':
            num_braces += 1
            in_tuple = 0
            new_str.extend(['[', *new_line()])
            continue
        elif char == ']':
            num_braces -= 1
            in_tuple = 0
            new_str.extend([']', *new_line()])
            continue
        elif char == '}':
            in_tuple = 0
        elif char == '(':
            in_tuple += 1
        elif char == ')':
            in_tuple -= 1

        if str_[i:i + 3] == ', [':
            num_braces += 1
            in_tuple = 0
            new_str.extend([', [', *new_line()])
            skip.extend(range(i, i + 3))
            continue
        if str_[i:i + 2] == ', ':
            new_str.extend([',', *new_line()])
            if in_tuple > 0:
                new_str.append(' ')
            skip.extend(range(i, i + 2))
            continue

        new_str.append(char)

    new_str.append('\n')
    return ''.join(new_str)


def p(obj):
    print(printable(obj))


def write():
    with open('out.py', 'w') as f:
        f.write(printable(window))


app = QApplication([])
window = Dialog()
window.show()
write()
sys.exit(app.exec_())
