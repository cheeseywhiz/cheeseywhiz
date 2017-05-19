"""
cd Desktop\projectEuler
cls
py firstWidget.pyw

"""
import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyautogui import *

class MainWidget(QWidget):
	def __init__(self):
		self.title = 'Project Euler'
		self.w = 250
		self.h = 150
		
		super().__init__()
		self.initUI()
	
	def initUI(self):
		self.setWindowTitle(self.title)
		self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
		self.setLayout(MainLayout())
		self.setFixedSize(self.sizeHint())
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

class MainLayout(QVBoxLayout):
	def __init__(self):
		super().__init__()
		self.initLayout()
	
	def initLayout(self):
		self.addWidget(MouseMovePositionText())

class MouseMovePositionText(QLabel):
	def __init__(self):
		with open('cities') as file: self.cities=eval(file.read())

		super().__init__()
		self.setAlignment(Qt.AlignCenter)
		
		self.setFixedWidth(200)
		
		self.old = None
		self.loop = QTimer()
		self.loop.timeout.connect(self.Loop)
		self.Loop()
		self.loop.start(1)

	def Loop(self):
		self.new = position()
		if self.new != self.old:
			self.setText(self.updatePosition())
	
	def updatePosition(self):
		self.old = position()
		pos = self.old
		N = 90-(15*pos[1]/64)
		E = (3294289897511*pos[0]/12500000000000)-180
		distances = [(N-city[1][0])**2+(E-city[1][1])**2 for city in self.cities]
		index = distances.index(min(distances))
		city = self.cities[index]
		distance = distances[index]
		output = "Mouse: %dN, %dE\n\n%s: %dN, %dE\nDistance:%d"%(N,E,city[0],city[1][0],city[1][1],math.sqrt(distance))
		return output

class Window(MainWidget):
	def __init__(self):
		background = QApplication(sys.argv)
		super().__init__()
		self.show()
		sys.exit(background.exec_())

class main(Window):
	def __init__(self):
		super().__init__()

if __name__ == '__main__': main()