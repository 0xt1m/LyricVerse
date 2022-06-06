from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class LabelForConstructor(QLabel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.init_ui()


	def init_ui(self):
		print("alright")
		self.setText("alright")
		self.move(10, 10)


	


	# def mousePressEvent(self, event):
	# 	cursor = QCursor()
	# 	print(cursor.pos().x())


	# def mouseMoveEvent(self, event):
	# 	cursor = QCursor()
	# 	self.move(cursor.pos().x(), cursor.pos().y())
	# 	self.setGeometry(cursor.pos().x(), cursor.pos().y(), 10, 10)




class ConstructorFrame(QFrame):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.init_ui()


	def init_ui(self):
		self.setGeometry(350, 110, 384, 216)
		self.setStyleSheet("border: 1px solid black")

		self.label = LabelForConstructor(self)

		self.label.move(20, 20)


	def mousePressEvent(self, QMouseEvent):
		cursor = QCursor()
		cursor_pos = self.label.mapFromGlobal(cursor.pos())
		print(cursor_pos.x(), cursor_pos.y())
		self.label.move(cursor_pos.x(), cursor_pos.y())
		print(cursor_pos.x(), cursor_pos.y())





