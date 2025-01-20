from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class LabelForConstructor(QLabel):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.parent = parent
		self.setGeometry(0, 0, 0, 0)
		# self.init_ui()


	def init_ui(self):
		frame_center_x = self.parent.width() / 2
		frame_center_y = self.parent.height() / 2
		self.move(frame_center_x - self.width() / 2, frame_center_y - self.height() / 2)


	def moveToCenter(self):
		self.adjustSize()
		frame_center_x = self.parent.width() / 2
		frame_center_y = self.parent.height() / 2
		print(frame_center_y, frame_center_x)
		self.move(frame_center_x - self.width() / 2, frame_center_y - self.height() / 2)


	def mousePressEvent(self, event):
		pass



	def mouseMoveEvent(self, event):
		cursor = QCursor()
		cursor_pos = self.parent.mapFromGlobal(cursor.pos())
		x = cursor_pos.x()
		y = cursor_pos.y()
		frame_center_x = self.parent.width() / 2
		frame_center_y = self.parent.height() / 2
		label_pos_x = x - (self.width() / 2)
		label_pos_y = y - (self.height() / 2)
		# if x >= self.width() / 2 and x < self.parent.width() - self.width() / 2 and y >= self.height() / 2 and y < self.parent.height() - self.height() / 2:
		
		if x >= frame_center_x - 10 and x <= frame_center_x + 10:
			label_pos_x = round(self.parent.width() / 2 - (self.width() / 2))

		if y >= frame_center_y - 10 and y <= frame_center_y + 10:
			label_pos_y = round(self.parent.height() / 2 - (self.height() / 2))

		if x + self.width() / 2 >= self.parent.width():
			label_pos_x = self.parent.width() - self.width()

		if x - self.width() / 2 <= 0:
			label_pos_x = 0

		if y + self.height() / 2 >= self.parent.height():
			label_pos_y = self.parent.height() - self.height()

		if y - self.height() / 2 <= 0:
			label_pos_y = 0
		
		self.move(label_pos_x, label_pos_y)




class ConstructorFrame(QFrame):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.init_ui()


	def init_ui(self):
		self.setGeometry(350, 110, 384, 216)
		self.setStyleSheet("border: 1px solid black")

		self.label = LabelForConstructor(self)






