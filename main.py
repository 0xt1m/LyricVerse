from design import Ui_MainWindow
from other_window import Ui_OtherWindow

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget

import sys

class ScreenShower(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()

	def init_ui(self):
		self.ui.btn_print.clicked.connect(self.open_window)

	def print_on(self):
		print("blablabla")

	def get_screens(self):
		# screenres = QRect()
		screens = QDesktopWidget().screenCount()
		print(screens)

	def open_window(self):
		self.window = QtWidgets.QMainWindow()
		self.ui = Ui_OtherWindow()
		self.ui.setupUi(self.window)
		self.window.setWindowFlags(Qt.FramelessWindowHint)
		self.window.showMaximized()


if __name__ == "__main__":
	app =  QtWidgets.QApplication([]) #QtWidgets.QApplication([])
	application = ScreenShower()
	display_monitor = 1
	monitor = QDesktopWidget().screenGeometry(display_monitor)
	application.move(monitor.left(), monitor.top())
	application.show()

	sys.exit(app.exec())







