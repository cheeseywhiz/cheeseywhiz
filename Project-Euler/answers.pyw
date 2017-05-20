import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

with open('answers') as file:
    answers = eval(file.read())


class MainWidget(QWidget):
    def __init__(self):
        self.title = 'Project Euler Answers'

        super().__init__()

        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.WindowCloseButtonHint |
                            Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle(self.title)
        self.setLayout(MainLayout())
        self.setFixedSize(self.sizeHint())


class MainLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.calculate_button = CalculateButton(self)
        self.line_input = LineInput(self)
        self.answer = QLabel()

        self.connectSignal(self.calculate_button)
        self.connectSignal(self.line_input)
        self.initLayout()

    def initLayout(self):
        row0layout = QHBoxLayout()
        row0layout.addWidget(QLabel('Question number:'))
        row0layout.addWidget(self.calculate_button)
        row0layout.setContentsMargins(0, 0, 0, 0)

        row0 = QWidget()
        row0.setLayout(row0layout)

        self.addWidget(row0)
        self.addWidget(self.line_input)
        self.answer.setAlignment(Qt.AlignRight)
        self.addWidget(self.answer)

    def connectSignal(self, source):
        source.calculateEvent.connect(self.updateAnswer)

    def updateAnswer(self, self_):
        if self_.line_input.text() in answers.keys():
            self_.answer.setText(answers[self_.line_input.text()])
        else:
            self_.answer.setText('Invalid question number')


class CalculateButton(QPushButton):
    calculateEvent = pyqtSignal('QObject')

    def __init__(self, caller):
        self.caller = caller
        super().__init__()
        self.setText('Calculate')
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.calculateEvent.emit(self.caller)


class LineInput(QLineEdit):
    calculateEvent = pyqtSignal('QObject')

    def __init__(self, caller):
        self.caller = caller
        super().__init__()
        self.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.calculateEvent.emit(self.caller)
        self.selectAll()

    def mousePressEvent(self, event):
        self.selectAll()


class Main(MainWidget):
    def __init__(self):
        app = QApplication(sys.argv)
        super().__init__()
        self.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    Main()
