from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from PyQt5.QtCore import Qt

from custom_item import CustomItem
from song import SongItem

import json
import sqlite3


class AddSongWindow(QMainWindow):
	def __init__(self, songbook):
		super().__init__()
		self.ui = Ui_AddSongWindow()
		self.ui.setup_ui(self)
		self.init_ui()
		self.songbook = songbook

	def init_ui(self):
		self.ui.song_list.setSpacing(2)
		self.ui.add_couplet_btn.clicked.connect(self.add_couplet)
		self.ui.add_chorus_btn.clicked.connect(self.add_chorus)
		self.ui.add_bridge_btn.clicked.connect(self.add_bridge)
		self.ui.remove_item_btn.clicked.connect(self.remove_item)
		self.ui.song_list.itemDoubleClicked.connect(self.edit_song_item)
		self.ui.save_item_btn.clicked.connect(self.save_song_item)
		self.ui.add_song_btn.clicked.connect(self.add_song)

		self.ui.save_item_btn.setEnabled(False)

		self.chorus = ""
		self.chorus_item = None

		self.couplets = []
		self.bridges = []

		self.ui.song_list.setStyleSheet("""
			::item {
				background-color: white;
				border: 1px solid black;
				border-radius: 10px;
			}
			::item:selected{
				border: 2px solid #c5cc04;
			}
			""")


	def edit_song_item(self):
		self.ui.save_item_btn.setEnabled(True)
		current_item = self.ui.song_list.currentItem()
		self.ui.text_input.clear()
		self.ui.text_input.appendPlainText(current_item.text)


	def save_song_item(self):
		self.ui.save_item_btn.setEnabled(False)
		current_text = self.ui.text_input.toPlainText()
		current_item = self.ui.song_list.currentItem()
		current_item.text = current_text

		if current_item.item_type == "couplet":
			custom_item = CustomItem(current_text, "couplet")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)
		elif current_item.item_type == "chorus":
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.item_type == "chorus":
					custom_item = CustomItem(current_text, "chorus")
					x_item.setSizeHint(custom_item.sizeHint())
					self.ui.song_list.setItemWidget(x_item, custom_item)
					x_item.text = current_text
		elif current_item.item_type == "bridge":
			custom_item = CustomItem(current_text, "bridge")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)

		self.ui.text_input.clear()


	def addCustomItem(self, text, item_type):
		custom_item = CustomItem(text, item_type)
		simple_item = SongItem(text, item_type)
		if item_type != "bridge":
			simple_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		simple_item.setSizeHint(custom_item.sizeHint())

		self.ui.song_list.addItem(simple_item)
		self.ui.song_list.setItemWidget(simple_item, custom_item)


	def insertCustomItem(self, text, item_type, index):
		custom_item = CustomItem(text, item_type)
		simple_item = SongItem(text, item_type)
		if item_type != "bridge":
			simple_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		simple_item.setSizeHint(custom_item.sizeHint())

		self.ui.song_list.insertItem(index, simple_item)
		self.ui.song_list.setItemWidget(simple_item, custom_item)


	def add_couplet(self):
		couplet_text = self.ui.text_input.toPlainText().strip()
		if couplet_text:
			self.addCustomItem(couplet_text, "couplet")

			self.ui.text_input.clear()
			self.couplets.append(couplet_text)

			if self.chorus:
				self.addCustomItem(self.chorus, "chorus")


	def add_chorus(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		chorus_text = self.ui.text_input.toPlainText().strip()
		couplet_indeces = []
		for x in range(self.ui.song_list.count()):
			x_item = self.ui.song_list.item(x)
			if x_item.item_type == "couplet": couplet_indeces.append(x)
		if chorus_text and not self.chorus and couplet_indeces:
			for i in range(len(couplet_indeces)-1, -1, -1): 
				self.insertCustomItem(chorus_text, "chorus", couplet_indeces[i]+1)

			self.ui.text_input.clear()
			self.chorus = chorus_text
		elif self.chorus: 
			msg.setText("Приспів може бути тільки один") 
			msg.exec_()
		else: 
			msg.setText("Додайте хоча б один куплет") 
			msg.exec_()


	def add_bridge(self):
		bridge_text = self.ui.text_input.toPlainText().strip()
		if bridge_text:
			self.addCustomItem(bridge_text, "bridge")

			self.ui.text_input.clear()
			self.bridges.append(bridge_text)


	def remove_item(self):
		current_item_index = self.ui.song_list.currentRow()
		if current_item_index != -1:
			item = self.ui.song_list.item(current_item_index)
			if item.item_type == "chorus":
				self.chorus = ""
				chorus_indeces = []
				for x in range(self.ui.song_list.count()):
					x_item = self.ui.song_list.item(x)
					if x_item.item_type == "chorus": chorus_indeces.append(x)
				for i in range(len(chorus_indeces)-1, -1, -1): self.ui.song_list.takeItem(chorus_indeces[i])

			elif item.item_type == "couplet":
				self.ui.song_list.takeItem(current_item_index)
				if self.chorus: self.ui.song_list.takeItem(current_item_index)
				if self.chorus and self.ui.song_list.count() == 0: self.chorus = ""
			elif item.item_type == "bridge": self.ui.song_list.takeItem(current_item_index)


	def add_song(self):
		with open("Songbooks/songbooks.json", "r") as jsonfile:
			songbooks = json.load(jsonfile)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Помилка")

		filename = songbooks[self.songbook]["filename"]

		song_title = self.ui.song_title.text()
		is_song_text = self.ui.song_list.count()
		if not song_title:
			msg.setText("Пісня не може бути без заголовка!")
			msg.exec_()
		elif not is_song_text:
			msg.setText("Пісня не може бути без тексту!")
			msg.exec_()
		else:
			couplets = []
			chorus = ""
			bridges = []
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.item_type == "couplet": couplets.append(x_item.text)
				elif not chorus and x_item.item_type == "chorus": chorus = x_item.text
				elif x_item.item_type == "bridge": bridges.append({"text": x_item.text, "index": x})


			song_text = {
				"Couplets": couplets,
				"Chorus": chorus,
				"Bridges": bridges
			}
			song_text = json.dumps(song_text, indent=4)

			connection = sqlite3.connect(f"Songbooks/{filename}")
			cursor = connection.cursor()
			cursor.execute(f"INSERT INTO Songs (title, song_text) VALUES ('{song_title}', '{song_text}')")
			connection.commit()

			self.close()


class Ui_AddSongWindow(object):
    def setup_ui(self, addSongWindow):
        addSongWindow.setObjectName("addSongWindow")
        addSongWindow.resize(738, 540)
        addSongWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(addSongWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.song_title = QtWidgets.QLineEdit(self.centralwidget)
        self.song_title.setGeometry(QtCore.QRect(10, 10, 310, 20))
        self.song_title.setObjectName("song_title")
        self.add_couplet_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_couplet_btn.setGeometry(QtCore.QRect(10, 320, 111, 23))
        self.add_couplet_btn.setObjectName("add_couplet_btn")
        self.add_chorus_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_chorus_btn.setGeometry(QtCore.QRect(120, 320, 111, 23))
        self.add_chorus_btn.setObjectName("add_chorus_btn")
        self.add_bridge_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_bridge_btn.setGeometry(QtCore.QRect(120, 350, 111, 23))
        self.add_bridge_btn.setObjectName("add_bridge_btn")
        self.song_list = QtWidgets.QListWidget(self.centralwidget)
        self.song_list.setGeometry(QtCore.QRect(330, 10, 401, 521))
        self.song_list.setDragEnabled(False)
        self.song_list.setDragDropOverwriteMode(False)
        self.song_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.song_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.song_list.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.song_list.setUniformItemSizes(False)
        self.song_list.setObjectName("song_list")
        self.text_input = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.text_input.setGeometry(QtCore.QRect(10, 130, 301, 181))
        self.text_input.setObjectName("text_input")
        self.add_song_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_song_btn.setGeometry(QtCore.QRect(80, 480, 141, 41))
        self.add_song_btn.setObjectName("add_song_btn")
        self.remove_item_btn = QtWidgets.QPushButton(self.centralwidget)
        self.remove_item_btn.setGeometry(QtCore.QRect(10, 350, 111, 23))
        self.remove_item_btn.setObjectName("remove_item_btn")
        self.save_item_btn = QtWidgets.QPushButton(self.centralwidget)
        self.save_item_btn.setGeometry(QtCore.QRect(230, 320, 75, 23))
        self.save_item_btn.setObjectName("save_item_btn")
        addSongWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(addSongWindow)
        QtCore.QMetaObject.connectSlotsByName(addSongWindow)

    def retranslateUi(self, addSongWindow):
        _translate = QtCore.QCoreApplication.translate
        addSongWindow.setWindowTitle(_translate("addSongWindow", "Нова пісня"))
        self.song_title.setPlaceholderText(_translate("addSongWindow", "Назва пісні"))
        self.add_couplet_btn.setText(_translate("addSongWindow", "Додати куплет"))
        self.add_chorus_btn.setText(_translate("addSongWindow", "Додати приспів"))
        self.add_bridge_btn.setText(_translate("addSongWindow", "Додати брідж"))
        self.add_song_btn.setText(_translate("addSongWindow", "Додати пісню"))
        self.remove_item_btn.setText(_translate("addSongWindow", "Видалити елемент"))
        self.save_item_btn.setText(_translate("addSongWindow", "Зберегти"))

