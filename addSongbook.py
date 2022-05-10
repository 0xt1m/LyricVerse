import sys, os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QUrl, QFileInfo
from PyQt5.QtGui import QFont

from SPSongsImporter import importSongsFromSP

class FileLabel(QLabel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAcceptDrops(True)
		self.resize(400, 400)
		self.move(10, 60)
		self.setText("Drag the file here")
		self.setAlignment(QtCore.Qt.AlignCenter)
		self.setStyleSheet("border: 2px dashed black;")
		font = QFont("Arial", 30)
		self.setFont(font)


	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls:
			event.accept()
		else:
			event.ignore()


	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
		else:
			event.ignore()


	def dropEvent(self, event):
		font = QFont("Arial", 12)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()

			if len(event.mimeData().urls()) > 1:
				msg.setText("You can drag only one file!")	
				msg.exec_()
			else:
				url = event.mimeData().urls()[0]
				if url.isLocalFile():
					file = QFileInfo(str(url.toLocalFile()))
					if file.suffix() == "sps":
						self.setText(file.fileName())
						self.setFont(font)
					else:
						msg.setText("We can't recognize type of this file")	
						msg.exec_()
				
		else:
			event.ignore()



class AddSongbookWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.resize(420, 500)
		self.setWindowTitle("Add songbook")

		self.file = FileLabel(self)
		self.file.mousePressEvent = self.browseFiles

		self.label = QLabel(self)
		self.label.setText("Enter songbook title:")
		self.label.adjustSize()
		self.label.move(10, 10)

		self.songbook_title_input = QLineEdit(self)
		self.songbook_title_input.setPlaceholderText("Євангельські пісні")
		self.songbook_title_input.setGeometry(10, 30, 200, 20)

		self.add_btn = QPushButton("Save", self)
		self.add_btn.setGeometry(10, 465, 400, 30)
		self.add_btn.clicked.connect(self.add_songbook)


	def browseFiles(self, event):
		font = QFont("Arial", 12)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
		file = QFileInfo(file_name[0])
		if file.suffix() == "sps":
			self.file.setText(file.fileName())
			self.file.setFont(font)
		else:
			msg.setText("We can't recognize type of this file")	
			msg.exec_()


	def add_songbook(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")
		
		if self.songbook_title_input.text().strip() == "":
			msg.setText("Songbook must to have any title")	
			msg.exec_()
		elif self.file.text() == "Drag the file here":
			msg.setText("Songbook must to have any file")	
			msg.exec_()
		else:
			importSongsFromSP(self.file.text(), self.songbook_title_input.text().strip())
			self.close()

# if __name__ == "__main__":
# 	app = QApplication(sys.argv)

# 	window = Application()
# 	window.show()

	# sys.exit(app.exec_())