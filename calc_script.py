from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys

from calc import Ui_MainWindow

class Calculator(QMainWindow):
	def __init__(self):
		super(Calculator, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_UI()

	def init_UI(self):
		self.setWindowTitle("blablabla")
		self.ui.label_result.setText("5 + 5")
		self.ui.btnEqual.clicked.connect(self.calculator)

		self.ui.btn0.clicked.connect(lambda: self.add_char('0'))
		self.ui.btn1.clicked.connect(lambda: self.add_char('1'))
		self.ui.btn2.clicked.connect(lambda: self.add_char('2'))
		self.ui.btn3.clicked.connect(lambda: self.add_char('3'))
		self.ui.btn4.clicked.connect(lambda: self.add_char('4'))
		self.ui.btn5.clicked.connect(lambda: self.add_char('5'))
		self.ui.btn6.clicked.connect(lambda: self.add_char('6'))
		self.ui.btn7.clicked.connect(lambda: self.add_char('7'))
		self.ui.btn8.clicked.connect(lambda: self.add_char('8'))
		self.ui.btn9.clicked.connect(lambda: self.add_char('9'))

		self.ui.btnAdd.clicked.connect(lambda: self.add_char('+'))
		self.ui.btnMinus.clicked.connect(lambda: self.add_char('-'))
		self.ui.btnMult.clicked.connect(lambda: self.add_char('*'))
		self.ui.btnDiv.clicked.connect(lambda: self.add_char('/'))

		self.ui.btnClear.clicked.connect(self.clear)



	

	def add_char(self, char):
		self.ui.label_result.setText(self.ui.label_result.text() + char)


	def clear(self):
		self.ui.label_result.setText("")


	def calculator(self):
		expression = self.ui.label_result.text()
		try:
			res = eval(expression)
			self.ui.label_result.setText(str(res))
		except:
			self.ui.label_result.setText("Error")


app = QtWidgets.QApplication([])
application = Calculator()
application.show()

sys.exit(app.exec())
