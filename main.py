from design import Ui_MainWindow
# from words_window import Ui_WordsWindow

from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtCore import Qt, QUrl, QFileInfo
# from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidgetItem, QShortcut, QWidget, QGraphicsDropShadowEffect, QFileDialog, QMessageBox
# from PyQt5.QtGui import QTransform, QKeySequence, QFont, QFontMetrics, QColor

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from addSongbook import AddSongbookWindow
from addSongWindow import Ui_addSongWindow
from EditSongWindow import Ui_EditSongWindow
from mybible_handler import Mybible
from Song import Song

import sqlite3
import json

import sys
import time
import string


class smartLabel(QLabel):
	def __init__(self, screen):
		super().__init__(screen)

	def ownWordWrap(self, max_font_size=150):
		font_size = 2
		font = QFont("Arial", font_size)
		self.setFont(font)

		one_line_height = self.fontMetrics().boundingRect(self.text()).height()
		count_of_lines = len(self.text().split("\n"))
		current_height = one_line_height * count_of_lines

		ready_text = ""

		while current_height < self.size().height() - (font_size + (font_size / 2)) and font_size <= max_font_size:
			words = self.text().split()
			ready_text = ""
			active_text = ""
			for w in range(len(words)):
				current_width = self.fontMetrics().boundingRect(active_text + words[w] + " ").width()
				if current_width > self.size().width() - (font_size + (font_size / 2)):
					ready_text += active_text.strip() + "\n"
					active_text = ""
				active_text += words[w] + " "
			ready_text += active_text

			font_size += 2
			new_font = QFont("Arial", font_size)
			new_font.setBold(True)
			self.setFont(new_font)

			one_line_height = self.fontMetrics().boundingRect(ready_text).height()
			count_of_lines = len(ready_text.split("\n"))
			current_height = one_line_height * count_of_lines
			while current_height > self.size().height():				
				font_size -= 2
				new_font = QFont("Arial", font_size)
				new_font.setBold(True)
				self.setFont(new_font)
				
				one_line_height = self.fontMetrics().boundingRect(ready_text).height()
				current_height = one_line_height * count_of_lines

		self.setText(ready_text.strip())


class SongLine:
	def __init__(self, text, wholePart, index_from):
		self.text = text
		self.index_from = index_from
		self.wholePart = wholePart



class WordsWindow(QMainWindow):
	def __init__(self, screen_number):
		super().__init__()
		self.screen_number = screen_number
		self.init_ui()

	def init_ui(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		# self.setWindowFlags(Qt.WindowStaysOnTopHint)

		self.isShowing = False
		screen = "screen_" + str(self.screen_number)
		if settings[screen]["show_words"]:
			self.setObjectName("WordsWindow")
			if settings[screen]["stream_mode"]:
				background = settings[screen]["stream_mode_settings"]["background"]
			else:
				background = settings[screen]["simple_mode_settings"]["background"]
			styles = """#WordsWindow {
				background: %s;
			}
			""" % (background)
			self.setStyleSheet(styles)

			self.label = smartLabel(self)
			if settings[screen]["stream_mode"]:
				mode = "stream_mode_settings"
			else:
				mode = "simple_mode_settings"

			font_size = settings[screen][mode]["font_size"]
			text_color = settings[screen][mode]["text_color"]
			font_size_info = settings[screen][mode]["font_size_info"]
			text_color_info = settings[screen][mode]["text_color_info"]

			f = QFont("Arial", font_size)
			f.setBold(True)
			self.label.setStyleSheet(f"color: {text_color}")
			self.label.setFont(f)
			self.label.setText("")
			self.label.setTextFormat(QtCore.Qt.AutoText)
			self.label.setAlignment(QtCore.Qt.AlignCenter)

			self.label_info = QtWidgets.QLabel(self)
			self.label_info.setGeometry(QtCore.QRect(10, 10, 400, 400))
			f = QFont("Arial", font_size_info)
			f.setItalic(True)
			self.label_info.setFont(f)
			self.label_info.setStyleSheet(f"color: {text_color_info}")

			self.setShadow()

			self.quitSc = QShortcut(QKeySequence('Esc'), self)
			self.quitSc.activated.connect(ScreenShower.hide_text)

			monitor = QDesktopWidget().screenGeometry(self.screen_number)
			self.move(monitor.left(), monitor.top())

			self.showFullScreen()
			self.isShowing = True


	def setShadow(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		screen = "screen_" + str(self.screen_number)
		if settings[screen]["stream_mode"]:
			mode = "stream_mode_settings"
		else:
			mode = "simple_mode_settings"

		if settings[screen][mode]["shadow"]:
			shadow = QGraphicsDropShadowEffect()
			try:
				shadow.setBlurRadius(settings[screen][mode]["shadow_blur_radius"])
			except:
				shadow.setBlurRadius(15)
			try:
				x = settings[screen][mode]["shadow_offset"]["x"]
				y = settings[screen][mode]["shadow_offset"]["y"]
				shadow.setOffset(x, y)
			except:
				pass
			self.label.setGraphicsEffect(shadow)

			shadow2 = QGraphicsDropShadowEffect()
			try:
				shadow2.setBlurRadius(settings[screen][mode]["shadow_blur_radius"])
			except:
				shadow2.setBlurRadius(15)
			try:
				x = settings[screen][mode]["shadow_offset"]["x"]
				y = settings[screen][mode]["shadow_offset"]["y"]
				shadow2.setOffset(x, y)
			except:
				pass
			self.label_info.setGraphicsEffect(shadow2)
		else:
			shadow = QGraphicsDropShadowEffect()
			shadow.setBlurRadius(0)
			shadow.setOffset(0, 0)
			self.label.setGraphicsEffect(shadow)
			self.label_info.setGraphicsEffect(shadow)


class CustomItem(QWidget):
	def __init__(self, text, type_of_item):
		super().__init__()

		self.type_of_item = type_of_item
		self.text = text

		self.setObjectName("CustomItem")
		self.textQVBoxLayout = QVBoxLayout()
		self.textQVBoxLayout.setSpacing(7)
		if type_of_item != "part":
			self.textUp = QLabel()
			self.textUp.setObjectName("textUp")
		self.textDown = QLabel()
		self.textDown.setObjectName("textDown")
		if type_of_item != "part":
			self.textQVBoxLayout.addWidget(self.textUp)
		self.textQVBoxLayout.addWidget(self.textDown)

		self.textDown.setText(self.text)

		self.allQHBoxLayout = QHBoxLayout()
		self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 0)

		if type_of_item != "part":
			if type_of_item == "couplet":
				self.textUp.setText("Куплет")

			elif type_of_item == "chour":
				self.textUp.setText("Приспів")

			elif type_of_item == "bridge":
				self.textUp.setText("Брідж")



		self.setStyleSheet("""
			#textUp {
				color: #044c87;
			}
			#textDown {
				color: black;
			}
			""")

		self.setLayout(self.allQHBoxLayout)
	

class SongItem(QListWidgetItem):
	def __init__(self, text, type_of_item):
		super().__init__()

		self.type_of_item = type_of_item
		self.text = text


class AddSongWindow(QMainWindow):
	def __init__(self, songbook):
		super().__init__()
		self.ui = Ui_addSongWindow()
		self.ui.setupUi(self)
		self.init_ui()
		self.songbook = songbook

	def init_ui(self):
		self.ui.song_list.setSpacing(2)
		self.ui.add_couplet_btn.clicked.connect(self.add_couplet)
		self.ui.add_chour_btn.clicked.connect(self.add_chour)
		self.ui.add_bridge_btn.clicked.connect(self.add_bridge)
		self.ui.remove_item_btn.clicked.connect(self.remove_item)
		self.ui.song_list.itemDoubleClicked.connect(self.edit_song_item)
		self.ui.save_item_btn.clicked.connect(self.save_song_item)
		self.ui.add_song_btn.clicked.connect(self.add_song)

		self.ui.save_item_btn.setEnabled(False)

		self.chour = ""
		self.chour_item = None

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

		if current_item.type_of_item == "couplet":
			custom_item = CustomItem(current_text, "couplet")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)
		elif current_item.type_of_item == "chour":
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.type_of_item == "chour":
					custom_item = CustomItem(current_text, "chour")
					x_item.setSizeHint(custom_item.sizeHint())
					self.ui.song_list.setItemWidget(x_item, custom_item)
					x_item.text = current_text
		elif current_item.type_of_item == "bridge":
			custom_item = CustomItem(current_text, "bridge")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)

		self.ui.text_input.clear()


	def addCustomItem(self, text, type_of_item):
		custom_item = CustomItem(text, type_of_item)
		simple_item = SongItem(text, type_of_item)
		if type_of_item != "bridge":
			simple_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		simple_item.setSizeHint(custom_item.sizeHint())

		self.ui.song_list.addItem(simple_item)
		self.ui.song_list.setItemWidget(simple_item, custom_item)


	def insertCustomItem(self, text, type_of_item, index):
		custom_item = CustomItem(text, type_of_item)
		simple_item = SongItem(text, type_of_item)
		if type_of_item != "bridge":
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

			if self.chour:
				self.addCustomItem(self.chour, "chour")


	def add_chour(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		chour_text = self.ui.text_input.toPlainText().strip()
		couplet_indeces = []
		for x in range(self.ui.song_list.count()):
			x_item = self.ui.song_list.item(x)
			if x_item.type_of_item == "couplet": couplet_indeces.append(x)
		if chour_text and not self.chour and couplet_indeces:
			for i in range(len(couplet_indeces)-1, -1, -1): 
				self.insertCustomItem(chour_text, "chour", couplet_indeces[i]+1)

			self.ui.text_input.clear()
			self.chour = chour_text
		elif self.chour: 
			msg.setText("Chour is already exists") 
			msg.exec_()
		else: 
			msg.setText("Add one couplet please") 
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
			if item.type_of_item == "chour":
				self.chour = ""
				chour_indeces = []
				for x in range(self.ui.song_list.count()):
					x_item = self.ui.song_list.item(x)
					if x_item.type_of_item == "chour": chour_indeces.append(x)
				for i in range(len(chour_indeces)-1, -1, -1): self.ui.song_list.takeItem(chour_indeces[i])

			elif item.type_of_item == "couplet":
				self.ui.song_list.takeItem(current_item_index)
				if self.chour: self.ui.song_list.takeItem(current_item_index)
				if self.chour and self.ui.song_list.count() == 0: self.chour = ""
			elif item.type_of_item == "bridge": self.ui.song_list.takeItem(current_item_index)


	def add_song(self):
		with open("Songbooks/songbooks.json", "r") as jsonfile:
			songbooks = json.load(jsonfile)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		filename = songbooks[self.songbook]["filename"]

		song_title = self.ui.song_title.text()
		is_song_text = self.ui.song_list.count()
		if not song_title:
			msg.setText("Song must to have title!")
			msg.exec_()
		elif not is_song_text:
			msg.setText("Song must to have text!")
			msg.exec_()
		else:
			couplets = []
			chour = ""
			bridges = []
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.type_of_item == "couplet": couplets.append(x_item.text)
				elif not chour and x_item.type_of_item == "chour": chour = x_item.text
				elif x_item.type_of_item == "bridge": bridges.append({"text": x_item.text, "index": x})


			song_text = {
				"Couplets": couplets,
				"Chour": chour,
				"Bridges": bridges
			}
			song_text = json.dumps(song_text, indent=4)

			connection = sqlite3.connect(f"Songbooks/{filename}")
			cursor = connection.cursor()
			cursor.execute(f"INSERT INTO Songs (title, song_text) VALUES ('{song_title}', '{song_text}')")
			connection.commit()

			self.close()


class EditSongWindow(QMainWindow):
	def __init__(self, songbook, song):
		super().__init__()
		self.ui = Ui_EditSongWindow()
		self.ui.setupUi(self)
		self.songbook = songbook
		self.song = song
		self.init_ui()


	def init_ui(self):
		self.ui.song_list.setSpacing(2)
		self.ui.add_couplet_btn.clicked.connect(self.add_couplet)
		self.ui.add_chour_btn.clicked.connect(self.add_chour)
		self.ui.add_bridge_btn.clicked.connect(self.add_bridge)
		self.ui.remove_item_btn.clicked.connect(self.remove_item)
		self.ui.song_list.itemDoubleClicked.connect(self.edit_song_item)
		self.ui.save_item_btn.clicked.connect(self.save_song_item)
		self.ui.edit_song_btn.clicked.connect(self.edit_song)

		self.ui.save_item_btn.setEnabled(False)

		self.chour = ""

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

		
		self.ui.song_title.setText(self.song.title)

		song_text = json.loads(self.song.song_text)
		song_couplets = song_text["Couplets"]
		self.chour = song_text["Chour"]
		song_bridges = song_text["Bridges"]

		for couplet in song_couplets:
			self.addCustomItem(couplet, "couplet")
			if self.chour: self.addCustomItem(self.chour, "chour")

		for bridge in song_bridges: self.insertCustomItem(bridge["text"], "bridge", bridge["index"])


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

		if current_item.type_of_item == "couplet":
			custom_item = CustomItem(current_text, "couplet")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)
		elif current_item.type_of_item == "chour":
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.type_of_item == "chour":
					custom_item = CustomItem(current_text, "chour")
					x_item.setSizeHint(custom_item.sizeHint())
					self.ui.song_list.setItemWidget(x_item, custom_item)
					x_item.text = current_text
		elif current_item.type_of_item == "bridge":
			custom_item = CustomItem(current_text, "bridge")
			current_item.setSizeHint(custom_item.sizeHint())
			self.ui.song_list.setItemWidget(current_item, custom_item)

		self.ui.text_input.clear()


	def addCustomItem(self, text, type_of_item):
		custom_item = CustomItem(text, type_of_item)
		simple_item = SongItem(text, type_of_item)
		if type_of_item != "bridge":
			simple_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		simple_item.setSizeHint(custom_item.sizeHint())

		self.ui.song_list.addItem(simple_item)
		self.ui.song_list.setItemWidget(simple_item, custom_item)


	def insertCustomItem(self, text, type_of_item, index):
		custom_item = CustomItem(text, type_of_item)
		simple_item = SongItem(text, type_of_item)
		if type_of_item != "bridge":
			simple_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
		simple_item.setSizeHint(custom_item.sizeHint())

		self.ui.song_list.insertItem(index, simple_item)
		self.ui.song_list.setItemWidget(simple_item, custom_item)


	def add_couplet(self):
		couplet_text = self.ui.text_input.toPlainText().strip()
		if couplet_text:
			self.addCustomItem(couplet_text, "couplet")
			self.ui.text_input.clear()

			if self.chour: self.addCustomItem(self.chour, "chour")


	def add_chour(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		chour_text = self.ui.text_input.toPlainText().strip()
		couplet_indeces = []
		for x in range(self.ui.song_list.count()):
			x_item = self.ui.song_list.item(x)
			if x_item.type_of_item == "couplet": couplet_indeces.append(x)
		if chour_text and not self.chour and couplet_indeces:
			for i in range(len(couplet_indeces)-1, -1, -1):
				custom_item = CustomItem(chour_text, "chour")
				chour_item = SongItem(chour_text, "chour")
				chour_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
				chour_item.setSizeHint(custom_item.sizeHint())

				self.ui.song_list.insertItem(couplet_indeces[i]+1, chour_item)
				self.ui.song_list.setItemWidget(chour_item, custom_item)

			self.ui.text_input.clear()
			self.chour = chour_text
		elif self.chour: 
			msg.setText("Chour is already exists") 
			msg.exec_()
		else: 
			msg.setText("Add one couplet please") 
			msg.exec_()


	def add_bridge(self):
		bridge_text = self.ui.text_input.toPlainText().strip()
		if bridge_text:
			self.addCustomItem(bridge_text, "bridge")

			self.ui.text_input.clear()


	def remove_item(self):
		current_item_index = self.ui.song_list.currentRow()
		if current_item_index != -1:
			item = self.ui.song_list.item(current_item_index)
			if item.type_of_item == "chour":
				self.chour = ""
				chour_indeces = []
				for x in range(self.ui.song_list.count()):
					x_item = self.ui.song_list.item(x)
					if x_item.type_of_item == "chour": chour_indeces.append(x)
				for i in range(len(chour_indeces)-1, -1, -1): self.ui.song_list.takeItem(chour_indeces[i])

			elif item.type_of_item == "couplet":
				self.ui.song_list.takeItem(current_item_index)
				if self.chour: self.ui.song_list.takeItem(current_item_index)
				if self.chour and self.ui.song_list.count() == 0: self.chour = ""
			elif item.type_of_item == "bridge": self.ui.song_list.takeItem(current_item_index)


	def edit_song(self):
		with open("Songbooks/songbooks.json", "r") as jsonfile:
			songbooks = json.load(jsonfile)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Error")

		filename = songbooks[self.songbook]["filename"]

		song_title = self.ui.song_title.text().strip()
		is_song_text = self.ui.song_list.count()
		if not song_title:
			msg.setText("Song must to have title!")
			msg.exec_()
		elif not is_song_text:
			msg.setText("Song must to have text!")
			msg.exec_()
		else:
			couplets = []
			chour = ""
			bridges = []
			for x in range(self.ui.song_list.count()):
				x_item = self.ui.song_list.item(x)
				if x_item.type_of_item == "couplet": couplets.append(x_item.text)
				elif not chour and x_item.type_of_item == "chour": chour = x_item.text
				elif x_item.type_of_item == "bridge": bridges.append({"text": x_item.text, "index": x})


			song_text = {
				"Couplets": couplets,
				"Chour": chour,
				"Bridges": bridges
			}
			song_text = json.dumps(song_text, indent=4)

			connection = sqlite3.connect(f"Songbooks/{filename}")
			cursor = connection.cursor()
			cursor.execute(f"UPDATE Songs SET title=?, song_text=? WHERE id={self.song.number}", (song_title, song_text))
			connection.commit()

			self.close()


class ScreenShower(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()


	def init_ui(self):
		self.anyStreamMode = self.check_stream_mode()

		self.setFixedSize(650, 580)
		self.ui.song_search.textChanged.connect(self.searchSong)
		self.ui.list_songs.itemPressed.connect(self.getWords)
		self.ui.list_words.itemSelectionChanged.connect(self.showSong)
		self.ui.list_words.itemPressed.connect(self.showSong)
		self.ui.bible_verses_list.itemPressed.connect(self.showBible)
		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(self.hide_text)
		self.ui.screensCB.currentTextChanged.connect(self.set_settings_from_screen)
		self.ui.btn_save.clicked.connect(self.change_settings_for_screen)
		self.ui.btn_save.clicked.connect(self.set_settings_for_screen)
		self.ui.av_songbooks.currentTextChanged.connect(self.get_songs_from_songbook)
		self.ui.av_translations.currentTextChanged.connect(self.set_bible)
		self.ui.bible_books_list.itemSelectionChanged.connect(self.get_chapters)
		self.ui.bible_chapters_list.itemSelectionChanged.connect(self.get_verses)
		self.ui.bible_verses_list.setWordWrap(True)
		self.ui.book_input.textChanged.connect(self.search_book)
		self.ui.chapter_input.textChanged.connect(self.search_chapter)
		self.ui.verse_input.textChanged.connect(self.search_verse)
		self.ui.quick_bible_search.textChanged.connect(self.quick_search)
		self.ui.bible_search.textChanged.connect(self.search_in_bible)
		self.ui.new_song_btn.clicked.connect(self.new_song)
		self.ui.edit_song_btn.clicked.connect(self.edit_song)
		self.ui.add_songbook_btn.clicked.connect(self.add_songbook)

		self.ui.list_words.setSpacing(2)
		self.ui.list_words.setStyleSheet("""
			::item {
				background-color: white;
				border: 1px solid black;
				border-radius: 10px;
			}
			::item:selected{
				border: 2px solid #c5cc04;
			}
			""")

		with open("Songbooks/songbooks.json", "r") as json_file:
			self.songbooks = json.load(json_file)

		self.songbook_names = list(self.songbooks.keys())
		for s in self.songbook_names:
			self.ui.av_songbooks.addItem(s)

		self.get_songs_from_songbook()

		with open("Bible_translations/bible_translations.json", "r") as json_file:
			self.bible_translations = json.load(json_file)

		self.bible_translations_names = list(self.bible_translations.keys())
		for b in self.bible_translations_names:
			self.ui.av_translations.addItem(b)
		self.set_bible()

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(0, count_of_screens):
			self.ui.screensCB.addItem(str(i))

		self.bible_place = [None, None, None]
		self.lastShown = None
		self.streamModeChanged = False
		self.song = None

		self.set_settings_for_screen()
		self.open_window()


	def check_stream_mode(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		count_of_screens = QDesktopWidget().screenCount()
		for s in range(count_of_screens):
			if settings[f"screen_{s}"]["stream_mode"]:
				return True
		return False


	def add_songbook(self):
		self.add_songbook_window = AddSongbookWindow()
		self.add_songbook_window.show()

		self.add_songbook_window.closeEvent = self.updateSongbooks


	def updateSongbooks(self, event):
		with open("Songbooks/songbooks.json", "r") as json_file:
			self.songbooks = json.load(json_file)

		self.songbook_names = list(self.songbooks.keys())

		self.ui.av_songbooks.currentTextChanged.disconnect(self.get_songs_from_songbook)
		self.ui.av_songbooks.clear()
		for s in self.songbook_names:
			self.ui.av_songbooks.addItem(s)
		self.ui.av_songbooks.currentTextChanged.connect(self.get_songs_from_songbook)

		self.get_songs_from_songbook()


	def new_song(self):
		self.addsong = AddSongWindow(self.ui.av_songbooks.currentText())
		self.addsong.show()
		self.addsong.closeEvent = self.updateSongList


	def updateSongList(self, event):
		self.get_songs_from_songbook()
		self.searchSong()


	def edit_song(self):
		if self.song != None:
			self.editsong = EditSongWindow(self.ui.av_songbooks.currentText(), self.song)
			self.editsong.show()

			self.editsong.closeEvent = self.updateSongList
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setWindowTitle("Error")
			msg.setText("You have to select song that you want to edit!")
			msg.exec_()


	def set_bible(self):
		self.bible = Mybible("Bible_translations/%s" % (self.bible_translations[self.ui.av_translations.currentText()]["filename"]))
		self.ui.bible_books_list.clear()
		try:
			for book in self.bible.all_books:
				self.ui.bible_books_list.addItem(book.long_name)
		except:
			pass


	def get_chapters(self):
		book_name = self.ui.bible_books_list.currentItem().text()
		self.bible_place[0] = book_name
		book_number = self.bible.book_to_number(book_name)
		count_of_chapters = self.bible.count_of_chapters(book_number)

		self.ui.bible_chapters_list.clear()
		for i in range(1, count_of_chapters + 1):
			self.ui.bible_chapters_list.addItem(str(i))
		self.ui.bible_chapters_list.setCurrentRow(0)


	def get_verses(self):
		try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
		except: pass

		book_number = int(self.bible.book_to_number(self.ui.bible_books_list.currentItem().text()))
		try:
			chapter = int(self.ui.bible_chapters_list.currentItem().text())
			self.bible_place[1] = str(chapter)
			chapter_verses = self.bible.get_verses(book_number, chapter)
			self.ui.bible_verses_list.clear()
			counter = 1
			for v in chapter_verses:
				self.ui.bible_verses_list.addItem(str(counter) + ". " + v.text)
				counter += 1
		except:
			pass

		self.ui.bible_verses_list.setCurrentRow(0)
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)


	def search_book(self):
		reqest = self.ui.book_input.text()
		try:
			book_number = self.bible.book_to_number(reqest.split()[0])
			self.ui.bible_books_list.setCurrentRow(self.bible.get_book_index_by_number(book_number))
		except Exception as error:
			pass


	def search_chapter(self):
		request = self.ui.chapter_input.text()
		try:
			chapter = int(request)
			self.ui.bible_chapters_list.setCurrentRow(chapter - 1)
		except:
			pass


	def search_verse(self):
		try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
		except: pass

		request = self.ui.verse_input.text()
		try:
			verse = int(request)
			self.ui.bible_verses_list.setCurrentRow(verse - 1)
		except Exception as error:
			pass
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)


	def quick_search(self):
		reqest = self.ui.quick_bible_search.text()

		try:
			book = reqest.split()[0]
			self.ui.book_input.setText(book)
		except:
			self.ui.book_input.setText("")

		try:
			chapter = reqest.split()[1]
			self.ui.chapter_input.setText(chapter)
		except:
			self.ui.chapter_input.setText("")

		try:
			verse = reqest.split()[2]
			self.ui.verse_input.setText(verse)
		except:
			self.ui.verse_input.setText("")


	def search_in_bible(self):
		reqest = self.ui.bible_search.text()
		try:
			search_res = self.bible.find_by_text(reqest)
			book_index = self.bible.get_book_index_by_number(int(search_res.book_number))
			self.ui.bible_books_list.setCurrentRow(book_index)

			self.ui.bible_chapters_list.setCurrentRow(int(search_res.chapter) - 1)

			try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
			except: pass
			self.ui.bible_verses_list.setCurrentRow(int(search_res.verse) - 1)
		except Exception as error:
			pass


	def get_songs_from_songbook(self):
		try: self.ui.list_songs.itemSelectionChanged.disconnect(self.getWords)
		except: pass

		try: self.ui.list_words.itemSelectionChanged.disconnect(self.showSong)
		except: pass

		if self.ui.av_songbooks.currentText():
			current_songbook = self.ui.av_songbooks.currentText()
			self.connection = sqlite3.connect(f'Songbooks/{self.songbooks[current_songbook]["filename"]}')
			self.cursor = self.connection.cursor()
			song_names = self.cursor.execute("SELECT id, title FROM Songs").fetchall()

			self.ui.list_songs.clear()
			self.ui.list_words.clear()
			for i in song_names:
				self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

			self.ui.list_songs.itemSelectionChanged.connect(self.getWords)
			self.ui.list_words.itemSelectionChanged.connect(self.showSong)


	def getSong(self, song_number):
		filename = self.songbooks[self.ui.av_songbooks.currentText()]["filename"]
		db = sqlite3.connect(f"Songbooks/{filename}")
		sql = db.cursor()
		song = sql.execute(f"SELECT * FROM Songs WHERE id='{song_number}'").fetchall()
		number = song[0][0]
		title = song[0][1]
		song_text = song[0][2]

		return Song(number, title, song_text)


	def getWords(self):
		try: self.ui.list_songs.itemSelectionChanged.disconnect(self.getWords)
		except: pass
		self.ui.list_words.itemSelectionChanged.disconnect(self.showSong)

		song_number = int(self.ui.list_songs.currentItem().text().split()[0])

		self.song = self.getSong(song_number)
		song_text = json.loads(self.song.song_text)
		song_couplets = song_text["Couplets"]
		song_chour = song_text["Chour"]
		song_bridges = song_text["Bridges"]

		self.ui.list_words.clear()

		if self.anyStreamMode:
			song_parts = []
			for couplet in song_couplets:
				song_parts.append(couplet)
				if song_chour: song_parts.append(song_chour)
			for b in song_bridges: song_parts.insert(b["index"], b["text"])
				
			self.song_lines = []
			for part in range(len(song_parts)):
				part_lines = song_parts[part].split("\n")
				for line in part_lines: self.song_lines.append(SongLine(line, song_parts[part], part))

			for line in self.song_lines:
				line_custom_item = CustomItem(line.text, "part")
				line_item = SongItem(line.text, "part")
				line_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
				line_item.setSizeHint(line_custom_item.sizeHint())

				self.ui.list_words.addItem(line_item)
				self.ui.list_words.setItemWidget(line_item, line_custom_item)
		
		elif not self.anyStreamMode:
			for i in song_couplets:
				couplet_custom_item = CustomItem(i, "couplet")
				couplet_item = SongItem(i, "couplet")
				couplet_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
				couplet_item.setSizeHint(couplet_custom_item.sizeHint())

				self.ui.list_words.addItem(couplet_item)
				self.ui.list_words.setItemWidget(couplet_item, couplet_custom_item)
				if song_chour != "":
					chour_custom_item = CustomItem(song_chour, "chour")
					chour_item = SongItem(song_chour, "chour")
					chour_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
					chour_item.setSizeHint(chour_custom_item.sizeHint())

					self.ui.list_words.addItem(chour_item)
					self.ui.list_words.setItemWidget(chour_item, chour_custom_item)
			if song_bridges:
				for b in song_bridges:
					bridge_custom_item = CustomItem(b["text"], "bridge")
					bridge_item = SongItem(b["text"], "bridge")
					bridge_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
					bridge_item.setSizeHint(bridge_custom_item.sizeHint())

					self.ui.list_words.insertItem(b["index"], bridge_item)
					self.ui.list_words.setItemWidget(bridge_item, bridge_custom_item)

		self.ui.list_words.setCurrentRow(0)

		self.ui.list_words.itemSelectionChanged.connect(self.showSong)
		self.ui.list_songs.itemSelectionChanged.connect(self.getWords)


	def searchSong(self):
		def checkIn(text1, text2):
			def makeUniversalText(text):
				text = text.lower()
				unnecessarySymbols = [",", ".", "!", ";", "\n"]
				for sym in unnecessarySymbols:
					text = text.replace(sym, "")
				text = text.replace(" –", "")

				return text


			text1 = makeUniversalText(text1)
			text2 = makeUniversalText(text2)

			if text2 in text1:
				return True
			return False

		songs = self.cursor.execute("SELECT * FROM Songs").fetchall()
		res = []

		req = self.ui.song_search.text()
		if req.isdigit():
			req = int(req)
			res = self.cursor.execute(f"SELECT * FROM Songs WHERE id={req}").fetchall()
		else:
			for s in songs:
				song_text_json = json.loads(s[2])
				song_text = ""
				for c in song_text_json["Couplets"]:
					song_text += c + "\n\n"
				song_text += song_text_json["Chour"]
				if checkIn(song_text, req):
					res.append(s)

		self.ui.list_songs.clear()
		for i in res:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

		try:
			self.ui.list_songs.setCurrentRow(0)
		except:
			pass


	def closeEvent(self, event):
		self.close_window()


	def showSong(self):
		self.hide_text()
		try:
			self.screens[1]
		except:
			self.open_window()

		self.lastShown = "song"

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		count_of_screens = QDesktopWidget().screenCount()
		for s in range(count_of_screens):
			try:
				self.screens[s].label
			except:
				continue

			if self.screens[s].isShowing == False:
				self.open_window()

			screen_size = QDesktopWidget().availableGeometry(s)
			screen = "screen_" + str(s)
			if settings[screen]["stream_mode"] and settings[screen]["show_words"]:
				font_size = settings[screen]["stream_mode_settings"]["font_size"]
				f = QFont("Arial", font_size)
				f.setBold(True)
				self.screens[s].label.setFont(f)

				line = self.ui.list_words.currentItem().text
				self.screens[s].label.setText(line)

				one_line_height = self.screens[s].label.fontMetrics().boundingRect(self.screens[s].label.text()).height()
				label_width = screen_size.width() - settings[screen]["stream_mode_settings"]["horizontal_margins"]
				screen_center_x = screen_size.width() / 2
				label_center_x = label_width / 2
				margin_bottom = settings[screen]["stream_mode_settings"]["margin_bottom"]
				self.screens[s].label.setGeometry(
					screen_center_x - label_center_x, screen_size.height() - margin_bottom,
					label_width, one_line_height
				)
				self.screens[s].setShadow()
				self.screens[s].label.ownWordWrap(font_size)

			elif settings[screen]["show_words"] and not settings[screen]["stream_mode"]:
				if self.anyStreamMode:
					lineIndex = self.ui.list_words.currentRow()
					part = self.song_lines[lineIndex].wholePart
				else:
					part = self.ui.list_words.currentItem().text
				self.screens[s].label.setText(part)

				font_size = settings[screen]["simple_mode_settings"]["font_size"]

				label_width = screen_size.width() - settings[screen]["simple_mode_settings"]["song_margins"]["h"]
				label_height = screen_size.height() - settings[screen]["simple_mode_settings"]["song_margins"]["v"]

				# Set label to center
				label_center_x = label_width / 2
				label_center_y = label_height / 2
				screen_center_x = screen_size.width() / 2
				screen_center_y = screen_size.height() / 2
				self.screens[s].label.setGeometry(
					screen_center_x - label_center_x,
					screen_center_y - label_center_y,
					label_width,
					label_height
				)
				self.screens[s].setShadow()
				# Set fit font
				self.screens[s].label.ownWordWrap(font_size)


	def showBible(self):
		try:
			self.screens[1]
		except:
			self.open_window()

		self.lastShown = "bible"

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		count_of_screens = QDesktopWidget().screenCount()
		for s in range(count_of_screens):
			try:
				self.screens[s].label
			except:
				continue

			if self.screens[s].isShowing == False:
				self.open_window()

			screen_size = QDesktopWidget().availableGeometry(s)
			screen = "screen_" + str(s)
			self.bible_place[2] = str(self.ui.bible_verses_list.currentRow() + 1)
			if settings[screen]["stream_mode"] and settings[screen]["show_words"]:
				font_size = settings[screen]["stream_mode_settings"]["font_size"]
				f = QFont("Arial", font_size)
				f.setBold(True)
				self.screens[s].label.setFont(f)

				self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

				bible_position = settings[screen]["stream_mode_settings"]["bible_position"]
				bible_size = settings[screen]["stream_mode_settings"]["bible_size"]

				label_center_x = bible_size["width"] / 2
				label_center_y = bible_size["height"] / 2
				self.screens[s].label.setGeometry(
					bible_position["x"] - label_center_x,
					bible_position["y"] - label_center_y,
					bible_size["width"],
					bible_size["height"]
				)

				self.screens[s].setShadow()
				self.screens[s].label.ownWordWrap(font_size)

				bible_place = self.list_to_bible_place(self.bible_place)
				self.screens[s].label_info.setText(bible_place)
				self.screens[s].label_info.adjustSize()

				info_position = settings[screen]["stream_mode_settings"]["info_position"]
				self.screens[s].label_info.move(int(info_position["x"]), int(info_position["y"]))
				font_size = settings[screen]["stream_mode_settings"]["font_size_info"]
				f = QFont("Arial", font_size)
				f.setItalic(True)
				self.screens[s].label_info.setFont(f)

			elif settings[screen]["show_words"] and not settings[screen]["stream_mode"]:
				self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

				font_size = settings[screen]["simple_mode_settings"]["font_size"]
				f = QFont("Arial", font_size)
				f.setBold(True)
				self.screens[s].label.setFont(f)

				label_width = screen_size.width() - settings[screen]["simple_mode_settings"]["bible_margins"]["h"]
				label_height = screen_size.height() - settings[screen]["simple_mode_settings"]["bible_margins"]["v"]

				# Set label to center
				label_center_x = label_width / 2
				label_center_y = label_height / 2
				screen_center_x = screen_size.width() / 2
				screen_center_y = screen_size.height() / 2
				self.screens[s].label.setGeometry(
					screen_center_x - label_center_x,
					screen_center_y - label_center_y,
					label_width,
					label_height
				)
				self.screens[s].setShadow()
				# Set fit font
				self.screens[s].label.ownWordWrap(font_size)

				bible_place = self.list_to_bible_place(self.bible_place)
				self.screens[s].label_info.setText(bible_place)
				self.screens[s].label_info.adjustSize()

				info_position = settings[screen]["simple_mode_settings"]["info_position"]
				self.screens[s].label_info.move(info_position["x"], info_position["y"])
				font_size = settings[screen]["simple_mode_settings"]["font_size_info"]
				f = QFont("Arial", font_size)
				f.setItalic(True)
				self.screens[s].label_info.setFont(f)


	def list_to_bible_place(self, l):
		res = ""
		for i in range(len(l)):
			if i == 0:
				res += str(l[i]) + " "
			if i == 1:
				res += str(l[i]) + ":"
			if i == 2:
				res += str(l[i])
		return res


	def open_window(self):
		self.screens = []

		# self.ui.screensCB.clear()
		count_of_screens = QDesktopWidget().screenCount()
		for i in range(count_of_screens):
			self.screens.append(WordsWindow(i))
			# self.ui.screensCB.addItem(str(i))


	def close_window(self):
		try: self.screens[1]
		except: return

		for s in self.screens:
			try: s.close()
			except: pass

		try: self.addsong.close()
		except: pass

		try: self.add_songbook_window.close()
		except: pass


	def hide_text(self):
		try:
			self.screens[1]
		except:
			return

		for s in self.screens:
			if s.isShowing:
				s.label.setText("")
				try:
					s.label_info.setText("")
				except:
					pass


	def set_settings_from_screen(self):
		screen_number = self.ui.screensCB.currentText()
		screen = "screen_" + str(screen_number)

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		try:
			settings[screen]["show_words"]
		except:
			return

		if settings[screen]["stream_mode"]:
			self.ui.settings_mode_tabs.setCurrentIndex(1)
		else:
			self.ui.settings_mode_tabs.setCurrentIndex(0)

		self.ui.checkbox_show_words.setChecked(settings[screen]["show_words"])
		self.ui.font_size_input.setValue(settings[screen]["simple_mode_settings"]["font_size"])
		self.ui.text_color_input.setText(settings[screen]["simple_mode_settings"]["text_color"])
		self.ui.shadow_checkbox.setChecked(settings[screen]["simple_mode_settings"]["shadow"])

		self.ui.checkbox_stream_mode.setChecked(settings[screen]["stream_mode"])
		self.ui.font_size_input_stream.setValue(settings[screen]["stream_mode_settings"]["font_size"])
		self.ui.text_color_input_stream.setText(settings[screen]["stream_mode_settings"]["text_color"])
		self.ui.shadow_checkbox_stream.setChecked(settings[screen]["stream_mode_settings"]["shadow"])


	def change_settings_for_screen(self):
		self.hide_text()
		self.ui.list_words.itemSelectionChanged.disconnect(self.showSong)

		screen_number = self.ui.screensCB.currentText()
		screen = "screen_" + str(screen_number)

		show_words = bool(self.ui.checkbox_show_words.checkState())
		text_color = self.ui.text_color_input.text()
		font_size = self.ui.font_size_input.value()
		shadow = bool(self.ui.shadow_checkbox.checkState())

		stream_mode = bool(self.ui.checkbox_stream_mode.checkState())
		text_color_stream = self.ui.text_color_input_stream.text()
		font_size_stream = self.ui.font_size_input_stream.value()
		shadow_stream = bool(self.ui.shadow_checkbox_stream.checkState())

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		try:
			settings[screen]["show_words"]
		except:
			return

		settings[screen]["show_words"] = show_words
		settings[screen]["simple_mode_settings"]["text_color"] = text_color
		settings[screen]["simple_mode_settings"]["font_size"] = font_size
		settings[screen]["simple_mode_settings"]["shadow"] = shadow

		if settings[screen]["stream_mode"] != stream_mode:
			self.streamModeChanged = True
		else:
			self.streamModeChanged = False

		settings[screen]["stream_mode"] = stream_mode
		settings[screen]["stream_mode_settings"]["text_color"] = text_color_stream
		settings[screen]["stream_mode_settings"]["font_size"] = font_size_stream
		settings[screen]["stream_mode_settings"]["shadow"] = shadow_stream

		with open("screens_settings.json", "w") as jsonfile:
			jsonfile.write(json.dumps(settings, indent=4))

		self.ui.list_words.itemSelectionChanged.connect(self.showSong)


	def set_settings_for_screen(self):
		self.anyStreamMode = self.check_stream_mode()

		if not self.streamModeChanged:
			if self.lastShown == None:
				self.hide_text()
			elif self.lastShown == "song":
				try:
					self.hide_text()
					self.showSong()
				except Exception as error:
					print(error)
					self.hide_text()
			elif self.lastShown == "bible":
				try:
					self.hide_text()
					self.showBible()
				except Exception as error:
					print(error)
					self.hide_text()
		else:
			self.open_window()
			self.hide_text()
			# self.getWords()

		self.ui.list_words.itemSelectionChanged.disconnect(self.showSong)

		screen_number = self.ui.screensCB.currentText()
		screen = "screen_" + str(screen_number)

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		if settings[screen]["show_words"]:
			self.open_window()
		else:
			self.close_window()

		if settings[screen]["stream_mode"]:
			self.ui.settings_mode_tabs.setCurrentIndex(1)
		else:
			self.ui.settings_mode_tabs.setCurrentIndex(0)

		self.ui.list_words.itemSelectionChanged.connect(self.showSong)



if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	application = ScreenShower()
	application.show()

	sys.exit(app.exec())
