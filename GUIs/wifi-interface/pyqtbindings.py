from PyQt5 import QtCore, QtWidgets


class QWidget(QtWidgets.QWidget):
    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.__layout = super().layout

    @property
    def layout(self):
        return self.__layout()

    @layout.setter
    def layout(self, layout):
        self.setLayout(layout)

    @property
    def minimum_size(self):
        return self.minimumSize()

    @minimum_size.setter
    def minimum_size(self, setter_args):
        if isinstance(setter_args, tuple):
            self.setMinimumSize(*setter_args)
        else:
            self.setMinimumSize(setter_args)

    @property
    def size_hint(self):
        return self.sizeHint()


class QCheckBox(QtWidgets.QCheckBox, QWidget):
    checked = QtCore.pyqtSignal()
    unchecked = QtCore.pyqtSignal()

    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.stateChanged.connect(self.handle_state_change)

    def handle_state_change(self, state):
        if state == QtCore.Qt.Checked:
            self.checked.emit()
        elif state == QtCore.Qt.Unchecked:
            self.unchecked.emit()

    @property
    def check_state(self):
        return self.checkState()

    @check_state.setter
    def check_state(self, state):
        self.setCheckState(state)


class QLineEdit(QtWidgets.QLineEdit, QWidget):
    def __init__(self, *base_args, **base_kwargs):
        super().__init__(*base_args, **base_kwargs)
        self.__font = super().font
        self.default_font = self.font

    @property
    def font(self):
        return self.__font()

    @font.setter
    def font(self, font):
        self.setFont(font)

    @property
    def echo_mode(self):
        return self.echoMode()

    @echo_mode.setter
    def echo_mode(self, mode):
        self.setEchoMode(mode)


class QMainWindow(QtWidgets.QMainWindow, QWidget):
    @property
    def window_title(self):
        return self.windowTitle()

    @window_title.setter
    def window_title(self, title):
        self.setWindowTitle(title)

    @property
    def central_widget(self):
        return self.centralWidget()

    @central_widget.setter
    def central_widget(self, widget):
        self.setCentralWidget(widget)


class QDialog(QtWidgets.QDialog, QWidget):
    @property
    def window_title(self):
        return self.windowTitle()

    @window_title.setter
    def window_title(self, title):
        self.setWindowTitle(title)


class QListWidget(QtWidgets.QListWidget, QWidget):
    def __getitem__(self, index):
        return self.indexWidget(index)

    @property
    def alternating_row_colors(self):
        return self.alternatingRowColors()

    @alternating_row_colors.setter
    def alternating_row_colors(self, enable):
        self.setAlternatingRowColors(enable)

    @property
    def horizontal_scroll_bar_policy(self):
        return self.horizontalScrollBarPolicy()

    @horizontal_scroll_bar_policy.setter
    def horizontal_scroll_bar_policy(self, policy):
        self.setHorizontalScrollBarPolicy(policy)

    @property
    def vertical_scroll_mode(self):
        return self.verticalScrollMode()

    @vertical_scroll_mode.setter
    def vertical_scroll_mode(self, mode):
        self.setVerticalScrollMode(mode)

    @property
    def selection_mode(self):
        return self.selectionMode()

    @selection_mode.setter
    def selection_mode(self, mode):
        self.setSelectionMode(mode)

    @property
    def current_index(self):
        return self.currentIndex()

    @current_index.setter
    def current_index(self, index):
        self.setCurrentIndex(index)


class QListWidgetItem(QtWidgets.QListWidgetItem, QWidget):
    @property
    def size_hint(self):
        return self.sizeHint()

    @size_hint.setter
    def size_hint(self, size):
        self.setSizeHint(size)


class QLayout(QtWidgets.QLayout):
    def __iadd__(self, widget):
        self.addWidget(widget)
        return self

    @property
    def contents_margins(self):
        return self.contentsMargins()

    @contents_margins.setter
    def contents_margins(self, setter_args):
        self.setContentsMargins(*setter_args)

    @property
    def size_constraint(self):
        return self.sizeConstraint()

    @size_constraint.setter
    def size_constraint(self, constraint):
        self.setSizeConstraint(constraint)

    @property
    def alignment_(self):
        return self.alignment()

    @alignment_.setter
    def alignment_(self, alignment):
        self.setAlignment(alignment)


class QHBoxLayout(QtWidgets.QHBoxLayout, QLayout):
    pass


class QVBoxLayout(QtWidgets.QVBoxLayout, QLayout):
    pass
