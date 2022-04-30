from design import Ui_MainWindow
# from words_window import Ui_WordsWindow

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidgetItem, QShortcut, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QTransform, QKeySequence, QFont, QFontMetrics

from configparser import ConfigParser
from mybible_handler import Mybible

import sqlite3
import json

import sys

class Song:
	def __init__(self, songbook, song_title):
		db = sqlite3.connect(f"Songbooks/{songbook}")
		self.sql = db.cursor()
		self.song = self.sql.execute(f"SELECT * FROM Songs WHERE title='{song_title}'").fetchall()
		self.song_text = self.song[0][2]
		song_text_lines = self.song_text.split("\n")
		self.song_list = []
		part_of_song = ""
		for t in range(0, len(song_text_lines)):
			if "куплет" in song_text_lines[t].lower() or "куплет:" in song_text_lines[t].lower() or "приспів" in song_text_lines[t].lower() or "приспів:" in song_text_lines[t].lower():
				if t != 0:
					self.song_list.append(part_of_song)
					part_of_song = ""
			part_of_song += song_text_lines[t] + "\n"
		self.song_list.append(part_of_song)

	def getSongList(self):
		return self.song_list

	def getCouplets(self):
		couplets = []
		for c in self.song_list:
			c_0 = c.split("\n")[0].lower()
			if "куплет" in c_0 or "куплет:" in c_0:
				c = c.split("\n")[1:]
				c = "\n".join(c)
				couplets.append(c.strip())

		return couplets

	def getChour(self):
		chour = ""
		for c in self.song_list:
			c_0 = c.split("\n")[0].lower()
			if "приспів" in c_0 or "приспів:" in c_0:
				c = c.split("\n")[1:]
				c = "\n".join(c)
				chour = c.strip()

		return chour


class WordsWindow(QMainWindow):
	def __init__(self, screen_number):
		super().__init__()
		self.screen_number = screen_number
		self.init_ui()

	def init_ui(self, ):
		config = ConfigParser()
		config.read("screens_config.ini")
		
		self.isShowing = False
		if config.get(f"screen_{self.screen_number}", "show_words") == "1":
			self.setObjectName("WordsWindow")
			styles = """#WordsWindow {
				background: %s;
			} 
			""" % (config[f'screen_{self.screen_number}']['background'])
			self.setStyleSheet(styles)

			self.label = QtWidgets.QLabel(self)
			f = QFont("Arial", int(config.get(f"screen_{self.screen_number}", "font_size")))
			f.setBold(True)
			self.label.setStyleSheet(f"color: {config[f'screen_{self.screen_number}']['text_color']}")
			self.label.setFont(f)
			self.label.setText("")
			self.label.setWordWrap(True)
			self.label.adjustSize()
			self.label.setTextFormat(QtCore.Qt.AutoText)
			self.label.setAlignment(QtCore.Qt.AlignCenter)

			self.label_info = QtWidgets.QLabel(self)
			self.label_info.setGeometry(QtCore.QRect(10, 10, 400, 400))
			f = QFont("Arial", int(config.get(f"screen_{self.screen_number}", "font_size_info")))
			f.setItalic(True)
			self.label_info.setFont(f)
			text_color = config.get(f"screen_{self.screen_number}", "color_info")
			self.label_info.setStyleSheet(f"color: {text_color}")

			self.quitSc = QShortcut(QKeySequence('Esc'), self)
			self.quitSc.activated.connect(ScreenShower.hide_text)

			monitor = QDesktopWidget().screenGeometry(self.screen_number)
			self.move(monitor.left(), monitor.top())

			self.showFullScreen()
			self.isShowing = True


class WordsWindowStream(QMainWindow):
	def __init__(self, screen_number):
		super().__init__()
		self.screen_number = screen_number
		self.init_ui()

	def init_ui(self):
		config = ConfigParser()
		config.read("screens_config.ini")
		
		self.isShowing = False
		if config.get(f"screen_{self.screen_number}", "show_words") == "1":
			self.setObjectName("WordsWindowStream")
			# styles = """
			# #WordsWindowStream {
			# 	background: %s;
			# } 
			# """ % (config[f'screen_{self.screen_number}']['background'])
			styles = "#WordsWindowStream {background-color: rgb(0,255,0)}"
			self.setStyleSheet(styles)

			self.label = QtWidgets.QLabel(self)
			self.label.setGeometry(QtCore.QRect(80, 480, 651, 61))
			f = QFont("Arial", int(config.get(f"screen_{self.screen_number}", "font_size")))
			f.setBold(True)
			self.label.setFont(f)
			
			self.label.setStyleSheet(f"""
				color: {config[f'screen_{self.screen_number}']['text_color']};\n
			""")
			self.label.setText("")
			self.label.setTextFormat(QtCore.Qt.AutoText)
			self.label.setAlignment(QtCore.Qt.AlignCenter)

			self.label_info = QtWidgets.QLabel(self)
			self.label_info.setGeometry(QtCore.QRect(10, 10, 400, 400))
			f = QFont("Arial", int(config.get(f"screen_{self.screen_number}", "font_size_info")))
			f.setItalic(True)
			self.label_info.setFont(f)

			text_color = config.get(f"screen_{self.screen_number}", "color_info")
			self.label_info.setStyleSheet(f"color: {text_color}")

			if config.get(f"screen_{self.screen_number}", "shadow") == "1":
				shadow = QGraphicsDropShadowEffect()
				try: 
					shadow.setBlurRadius(config.get(f"screen_{self.screen_number}", "shadow_blur_radius"))
				except:
					shadow.setBlurRadius(15)
				try:
					x = int(config.get(f"screen_{self.screen_number}", "shadow_offset").split()[0])
					y = int(config.get(f"screen_{self.screen_number}", "shadow_offset").split()[1])
					shadow.setOffset(x, y)
				except:
					pass
				self.label.setGraphicsEffect(shadow)

				shadow2 = QGraphicsDropShadowEffect()
				try: 
					shadow2.setBlurRadius(config.get(f"screen_{self.screen_number}", "shadow_blur_radius"))
				except:
					shadow2.setBlurRadius(15)
				try:
					x = int(config.get(f"screen_{self.screen_number}", "shadow_offset").split()[0])
					y = int(config.get(f"screen_{self.screen_number}", "shadow_offset").split()[1])
					shadow2.setOffset(x, y)
				except:
					pass
				self.label_info.setGraphicsEffect(shadow2)

			self.quitSc = QShortcut(QKeySequence('Esc'), self)
			self.quitSc.activated.connect(ScreenShower.hide_text)

			monitor = QDesktopWidget().screenGeometry(self.screen_number)
			self.move(monitor.left(), monitor.top())

			self.showFullScreen()
			self.isShowing = True


class ScreenShower(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()

	
	def init_ui(self):
		self.setFixedSize(650, 520)
		self.ui.song_search.textChanged.connect(self.searchSong)
		self.ui.list_songs.itemSelectionChanged.connect(self.getWords)
		self.ui.list_words.itemSelectionChanged.connect(self.showSong)
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
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)
		self.ui.bible_verses_list.itemPressed.connect(self.showBible)
		self.ui.book_input.textChanged.connect(self.search_book)
		self.ui.chapter_input.textChanged.connect(self.search_chapter)
		self.ui.verse_input.textChanged.connect(self.search_verse)
		self.ui.quick_bible_search.textChanged.connect(self.quick_search)
		self.ui.bible_search.textChanged.connect(self.search_in_bible)

		self.ui.list_words.setSpacing(5)

		with open("Songbooks/songbooks.json", "r") as json_file:
			self.songbooks = json.load(json_file)
		
		self.songbook_names = list(self.songbooks.keys())
		for s in self.songbook_names:
			self.ui.av_songbooks.addItem(s)

		self.get_songs_from_songbook()

		with open("bible_translations/bible_translations.json", "r") as json_file:
			self.bible_translations = json.load(json_file)
	
		self.bible_translations_names = list(self.bible_translations.keys())
		for b in self.bible_translations_names:
			self.ui.av_translations.addItem(b)
		self.set_bible()

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(0, count_of_screens):
			self.ui.screensCB.addItem(str(i))

		self.bible_place = [None, None, None]

		self.anyStreamMode = False
		self.set_settings_for_screen()
		self.open_window()

	
	def set_bible(self):
		self.bible = Mybible("bible_translations/%s" % (self.bible_translations[self.ui.av_translations.currentText()]["filename"]))
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
		self.hide_text()

	
	def get_verses(self):
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
		self.hide_text()

	
	def search_book(self):
		reqest = self.ui.book_input.text()
		try:
			book_number = self.bible.book_to_number(reqest.split()[0])
			self.ui.bible_books_list.setCurrentRow(self.bible.get_book_index_by_number(book_number))
			self.ui.bible_books_list.scrollToItem(self.ui.bible_books_list.currentItem())
		except Exception as error:
			self.ui.bible_books_list.setCurrentRow(0)
			self.ui.bible_books_list.scrollToItem(self.ui.bible_books_list.currentItem())


	def search_chapter(self):
		reqest = self.ui.chapter_input.text()
		try:
			chapter = int(reqest)
			self.ui.bible_chapters_list.setCurrentRow(chapter - 1)
			self.ui.bible_chapters_list.scrollToItem(self.ui.bible_chapters_list.currentItem())
		except:
			pass


	def search_verse(self):
		try:
			self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
		except:
			pass

		reqest = self.ui.verse_input.text()
		try:
			verse = int(reqest)
			self.ui.bible_verses_list.setCurrentRow(verse - 1)
			self.ui.bible_verses_list.scrollToItem(self.ui.bible_verses_list.currentItem())	
		except Exception as error:
			pass
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)

	
	def quick_search(self):
		self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
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

		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)


	def get_songs_from_songbook(self):
		self.connection = sqlite3.connect(f'Songbooks/{self.songbooks[self.ui.av_songbooks.currentText()]["filename"]}')
		self.cursor = self.connection.cursor()
		song_names = self.cursor.execute("SELECT id, title FROM Songs").fetchall()
		
		self.hide_text()
		self.ui.list_songs.clear()
		self.ui.list_words.clear()
		for i in song_names:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

		self.searchSong()

	
	def closeEvent(self, event):
		self.close_window()

	
	def showSong(self):
		self.hide_text()
		self.showWords("song")

	
	def showBible(self):
		self.showWords("bible")

	
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
			for song in songs: 
				if checkIn(song[2], req):
					res.append(song)
		
		self.ui.list_songs.clear()
		for i in res:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

		try:
			self.ui.list_songs.setCurrentRow(0)
		except:
			pass

	
	def search_in_bible(self):
		try:
			self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.showBible)
		except:
			pass

		reqest = self.ui.bible_search.text()
		try:
			search_res = self.bible.find_by_text(reqest)
			self.ui.bible_books_list.setCurrentRow(self.bible.get_book_index_by_number(int(search_res.book_number)))
			self.ui.bible_books_list.scrollToItem(self.ui.bible_books_list.currentItem())

			self.ui.bible_chapters_list.setCurrentRow(int(search_res.chapter) - 1)
			self.ui.bible_chapters_list.scrollToItem(self.ui.bible_chapters_list.currentItem())

			self.ui.bible_verses_list.setCurrentRow(int(search_res.verse) - 1)
			self.ui.bible_verses_list.scrollToItem(self.ui.bible_verses_list.currentItem())	
		except Exception as error:
			pass
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.showBible)
	

	def getWords(self):
		text_l = self.ui.list_songs.currentItem().text().split()
		text_l.pop(0)
		
		song_title = ""
		for t in text_l:
			song_title += t + " "
		song_title = song_title.strip()
		
		try:
			song = Song(self.songbooks[self.ui.av_songbooks.currentText()]["filename"], song_title)
			song_couplets = song.getCouplets()
			song_chour = song.getChour()

			self.ui.list_words.clear()
			
			self.song_list_parts = []
			self.song_list_lines = []
			for i in song_couplets:
				self.song_list_parts.append(i)
				if song_chour != "":
					self.song_list_parts.append(song_chour)
			
			if self.anyStreamMode:
				for part in range(len(self.song_list_parts)):
					for line in self.song_list_parts[part].split("\n"):
						self.song_list_lines.append(line + " " + str(part))

				for line in self.song_list_lines:
					self.ui.list_words.addItem(line[:-2])
			elif not self.anyStreamMode:
				self.ui.list_words.addItems(self.song_list_parts)
		except:
			pass
		self.hide_text()
	
	
	def scaleLabelContent(self, screen_number, width=None, height=None):
		config = ConfigParser()
		config.read("screens_config.ini")

		screen_size = QDesktopWidget().availableGeometry(screen_number)
		if width == None and height == None:
			width = screen_size.width() - 20
			height = screen_size.height() - 20
		
		self.screens[screen_number].label.setGeometry(0, 0, width, height)
		self.screens[screen_number].label.setWordWrap(True)
		self.screens[screen_number].label.adjustSize()
		label_size = self.screens[screen_number].label.size()
		font_size = int(config.get(f"screen_{screen_number}", "font_size"))
		while label_size.width() > width or label_size.height() > height:
			font_size -= 1
			new_font = QFont("Arial", font_size)
			new_font.setBold(True)
			self.screens[screen_number].label.setFont(new_font)
			self.screens[screen_number].label.adjustSize()
			label_size = self.screens[screen_number].label.size()

	
	def scaleLabelContentByHeight(self, screen_number, height=None):
		config = ConfigParser()
		config.read("screens_config.ini")

		screen_size = QDesktopWidget().availableGeometry(screen_number)
		if height == None:
			height = screen_size.height() - 20
		
		self.screens[screen_number].label.setGeometry(0, 0, screen_size.width() - 20, height)
		self.screens[screen_number].label.setWordWrap(False)
		self.screens[screen_number].label.adjustSize()
		label_size = self.screens[screen_number].label.size()
		font_size = int(config.get(f"screen_{screen_number}", "font_size"))
		while label_size.height() > height:
			font_size -= 1
			new_font = QFont("Arial", font_size)
			new_font.setBold(True)
			self.screens[screen_number].label.setFont(new_font)
			self.screens[screen_number].label.adjustSize()
			label_size = self.screens[screen_number].label.size()


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

	
	def showWords(self, words_type):
		try:
			self.screens[1]
		except:
			self.open_window()

		config = ConfigParser()
		config.read("screens_config.ini")

		count_of_screens = QDesktopWidget().screenCount()
		for s in range(count_of_screens):
			try:
				self.screens[s].label
			except:
				continue

			if self.screens[s].isShowing == False:
				self.open_window()

			screen_size = QDesktopWidget().availableGeometry(s)

			font_size = int(config.get(f"screen_{s}", "font_size"))
			f = QFont("Arial", font_size)
			f.setBold(True)
			self.screens[s].label.setFont(f)
			
			if self.anyStreamMode:
				try:
					if words_type == "song":
						partIndex = int(self.song_list_lines[self.ui.list_words.currentRow()].split().pop())
						if config.get(f"screen_{s}", "stream_mode") == "1" and config.get(f"screen_{s}", "show_words") == "1":
							line = self.ui.list_words.currentItem().text()
							self.screens[s].label.setText(line)
							self.screens[s].label.setGeometry(0, 0, screen_size.width(), 100)
							
							self.scaleLabelContentByHeight(s, 100)
							label_size = self.screens[s].label.size()
							screen_center_x = screen_size.width() / 2
							label_center_x = label_size.width() / 2
							margin_bottom = int(config.get(f"screen_{s}", "margin_bottom"))
							self.screens[s].label.setGeometry(
								screen_center_x - label_center_x, 
								screen_size.height() - margin_bottom, 
								label_size.width(), 
								label_size.height()
							)
					
						elif config.get(f"screen_{s}", "stream_mode") == "0" and config.get(f"screen_{s}", "show_words") == "1":
							part = self.song_list_parts[partIndex]
							self.screens[s].label.setText(part)

							self.scaleLabelContent(s, screen_size.width() - 200, screen_size.height() - 200)
							label_size = self.screens[s].label.size()
							screen_center_x = screen_size.width() / 2
							screen_center_y = screen_size.height() / 2
							label_center_x = label_size.width() / 2
							label_center_y = label_size.height() / 2
							self.screens[s].label.setGeometry(
								screen_center_x - label_center_x, 
								screen_center_y - label_center_y, 
								label_size.width(), 
								label_size.height()
							)
					elif words_type == "bible":
						self.bible_place[2] = str(self.ui.bible_verses_list.currentRow() + 1)
						if config.get(f"screen_{s}", "stream_mode") == "1" and config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

							bible_position = config.get(f"screen_{s}", "bible_position").split()
							bible_size = config.get(f"screen_{s}", "bible_size").split()
							self.scaleLabelContent(s, int(bible_size[0]), int(bible_size[1]))
							label_size = self.screens[s].label.size()
							label_center_x = label_size.width() / 2
							label_center_y = label_size.height() / 2
							self.screens[s].label.setGeometry(
								int(bible_position[0]) - label_center_x, 
								int(bible_position[1]) - label_center_y, 
								label_size.width(), 
								label_size.height()
							)
							bible_place = self.list_to_bible_place(self.bible_place)
							self.screens[s].label_info.setText(bible_place)
							self.screens[s].label_info.adjustSize()

							info_position = config.get(f"screen_{s}", "info_stream_position").split()
							self.screens[s].label_info.move(int(info_position[0]), int(info_position[1]))
							font_size = int(config.get(f"screen_{s}", "font_size_info"))
							f = QFont("Arial", font_size)
							f.setItalic(True)
							self.screens[s].label_info.setFont(f)

						elif config.get(f"screen_{s}", "stream_mode") == "0" and config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

							self.scaleLabelContent(s, screen_size.width() - 200, screen_size.height() - 200)
							label_size = self.screens[s].label.size()
							screen_center_x = screen_size.width() / 2
							screen_center_y = screen_size.height() / 2
							label_center_x = label_size.width() / 2
							label_center_y = label_size.height() / 2
							self.screens[s].label.setGeometry(
								screen_center_x - label_center_x, 
								screen_center_y - label_center_y, 
								label_size.width(), 
								label_size.height()
							)

							bible_place = self.list_to_bible_place(self.bible_place)
							self.screens[s].label_info.setText(bible_place)
							self.screens[s].label_info.adjustSize()

							info_position = config.get(f"screen_{s}", "info_position").split()
							self.screens[s].label_info.move(int(info_position[0]), int(info_position[1]))
							font_size = int(config.get(f"screen_{s}", "font_size_info"))
							f = QFont("Arial", font_size)
							f.setItalic(True)
							self.screens[s].label_info.setFont(f)
						
				except Exception as error:
					print(error)
			
			elif not self.anyStreamMode:
				try:
					if words_type == "song":
						part = self.ui.list_words.currentItem().text()
						if config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(part)
					elif words_type == "bible":
						self.bible_place[2] = str(self.ui.bible_verses_list.currentRow() + 1)
						bible_place = self.list_to_bible_place(self.bible_place)
						if config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

							bible_place = self.list_to_bible_place(self.bible_place)
							self.screens[s].label_info.setText(bible_place)
							self.screens[s].label_info.adjustSize()

							info_position = config.get(f"screen_{s}", "info_position").split()
							self.screens[s].label_info.move(int(info_position[0]), int(info_position[1]))
							font_size = int(config.get(f"screen_{s}", "font_size_info"))
							f = QFont("Arial", font_size)
							f.setItalic(True)
							self.screens[s].label_info.setFont(f)

					
					self.scaleLabelContent(s, screen_size.width() - 200, screen_size.height() - 200)
					label_size = self.screens[s].label.size()
					screen_center_x = screen_size.width() / 2
					screen_center_y = screen_size.height() / 2
					label_center_x = label_size.width() / 2
					label_center_y = label_size.height() / 2

					self.screens[s].label.setGeometry(
						screen_center_x - label_center_x, 
						screen_center_y - label_center_y, 
						label_size.width(), 
						label_size.height()
					)
				except Exception as error:
					print(error)


	def open_window(self):
		config = ConfigParser()
		config.read("screens_config.ini")

		self.screens = []

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(count_of_screens):
			stream_mode = bool(int(config.get(f"screen_{i}", "stream_mode")))
			if stream_mode:
				self.screens.append(WordsWindowStream(i))
			elif not stream_mode:
				self.screens.append(WordsWindow(i))

		# self.screens[1].label.setText("Hello")

	
	def close_window(self):
		try:
			self.screens[1]
		except:
			return
		
		for s in self.screens:
			if s.isShowing:
				s.isShowing = False
				s.close()	


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

		self.ui.checkbox_show_words.setChecked(False)
		self.ui.checkbox_stream_mode.setChecked(False)

		config = ConfigParser()
		config.read("screens_config.ini")

		try:
			config.get(f"screen_{screen_number}", "show_words")
		except:
			return

		show_words = bool(int(config.get(f"screen_{screen_number}", "show_words")))
		stream_mode = bool(int(config.get(f"screen_{screen_number}", "stream_mode")))

		if show_words:
			self.ui.checkbox_show_words.setChecked(True)
		if stream_mode:
			self.ui.checkbox_stream_mode.setChecked(True)


	def change_settings_for_screen(self):
		screen_number = self.ui.screensCB.currentText()
		
		show_words = "0"
		stream_mode = "0"
		if self.ui.checkbox_show_words.checkState():
			show_words = "1"
		if self.ui.checkbox_stream_mode.checkState():
			stream_mode = "1"
		
		
		config = ConfigParser()
		config.read("screens_config.ini")

		try:
			config.add_section(f"screen_{screen_number}")
		except:
			pass

		config.set(f"screen_{screen_number}", "show_words", show_words)
		config.set(f"screen_{screen_number}", "stream_mode", stream_mode)

		with open('screens_config.ini', 'w') as configfile:
			config.write(configfile)


	def set_settings_for_screen(self):
		screen_number = self.ui.screensCB.currentText()

		config = ConfigParser()
		config.read("screens_config.ini")

		show_words = bool(int(config.get(f"screen_{screen_number}", "show_words")))

		if show_words:
			self.open_window()
		else:
			self.hide_text()

		
		def check_stream_mode():
			count_of_screens = QDesktopWidget().screenCount()
			for s in range(count_of_screens):
				if config.get(f"screen_{s}", "stream_mode") == "1":
					return True
			return False

		self.anyStreamMode = check_stream_mode()

		try:
			self.getWords()
		except AttributeError:
			pass

		self.open_window()


	def change_config(self, key_one, key_two, value):
		config = ConfigParser()
		config.read("screens_config.ini")
		try:
			config.add_section(key_one)
		except:
			pass
		config.set(key_one, key_two, value)

		with open('screens_config.ini', 'w') as configfile:
			config.write(configfile)
	


if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	application = ScreenShower()
	application.show()

	sys.exit(app.exec())







