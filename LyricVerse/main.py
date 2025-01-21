from ui_main_window import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from add_songbook_window import AddSongbookWindow
from add_song_window import AddSongWindow
from edit_song_window import EditSongWindow

from words_window import WordsWindow

from mybible_handler import Mybible
from song import Song, SongItem, SongLine
from custom_item import CustomItem

import sqlite3
import json
import sys


class LyricVerse(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()


	def init_ui(self):
		self.anyStreamMode = self.check_stream_mode()
		self.setFixedSize(810, 580)
		self.ui.song_search.textChanged.connect(self.search_song)
		self.ui.list_songs.itemPressed.connect(self.get_words)
		self.ui.list_words.itemSelectionChanged.connect(self.show_song)
		self.ui.list_words.itemPressed.connect(self.show_song)
		self.ui.bible_verses_list.itemPressed.connect(self.show_bible)
		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(self.hide_text)
		self.ui.screensCB.currentTextChanged.connect(self.set_values)
		self.ui.btn_save.clicked.connect(self.set_settings)
		self.ui.available_songbooks_element.currentTextChanged.connect(self.get_songs_from_songbook)
		self.ui.av_translations.currentTextChanged.connect(self.set_bible)
		self.ui.bible_books_list.itemSelectionChanged.connect(self.set_chapters)
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
			self.ui.available_songbooks_element.addItem(s)

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
		self.last_shown_song = None
		self.screens = []

		self.set_settings()
		self.open_window()


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return:
			if self.ui.tabs.currentIndex() == 1 and self.ui.quick_bible_search.text().strip() or self.ui.bible_search.text().strip():
				try: self.show_bible()
				except: pass
			elif self.ui.tabs.currentIndex() == 0:
				try: self.show_song()
				except: pass


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

		self.ui.available_songbooks_element.currentTextChanged.disconnect(self.get_songs_from_songbook)
		self.ui.available_songbooks_element.clear()
		for s in self.songbook_names:
			self.ui.available_songbooks_element.addItem(s)
		self.ui.available_songbooks_element.currentTextChanged.connect(self.get_songs_from_songbook)

		self.get_songs_from_songbook()


	def new_song(self):
		self.add_song_window = AddSongWindow(self.ui.available_songbooks_element.currentText())
		self.add_song_window.show()
		self.add_song_window.closeEvent = self.updateSongList




	def edit_song(self):
		if self.song != None:
			self.editsong = EditSongWindow(self.ui.available_songbooks_element.currentText(), self.song)
			self.editsong.show()
			self.editsong.closeEvent = self.updateSongList

		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setWindowTitle("Помилка")
			msg.setText("Ви не вибрали пісню яку хочете редагувати!")
			msg.exec_()


	def updateSongList(self, event):
		self.get_songs_from_songbook()
		if self.song:
			self.ui.list_songs.setCurrentRow(self.song.number - 1)
		
		self.search_song()


	def set_bible(self):
		try:
			self.bible = Mybible("Bible_translations/%s" % (self.bible_translations[self.ui.av_translations.currentText()]["filename"]))
			self.ui.bible_books_list.clear()

			for book in self.bible.all_books:
				self.ui.bible_books_list.addItem(book.long_name)
		except Exception as e:
			print(e)


	def set_chapters(self):
		book_name = self.ui.bible_books_list.currentItem().text()
		self.bible_place[0] = book_name
		book_number = self.bible.book_to_number(book_name)
		count_of_chapters = self.bible.count_of_chapters(book_number)

		self.ui.bible_chapters_list.clear()
		for i in range(1, count_of_chapters + 1):
			self.ui.bible_chapters_list.addItem(str(i))
		
		self.ui.bible_chapters_list.setCurrentRow(0)


	def get_verses(self):
		try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.show_bible)
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
		except Exception as e:
			print(e)

		self.ui.bible_verses_list.setCurrentRow(0)
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.show_bible)


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
		try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.show_bible)
		except: pass

		request = self.ui.verse_input.text()
		try:
			verse = int(request)
			self.ui.bible_verses_list.setCurrentRow(verse - 1)
		except Exception as error:
			pass
		self.ui.bible_verses_list.itemSelectionChanged.connect(self.show_bible)


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

			try: self.ui.bible_verses_list.itemSelectionChanged.disconnect(self.show_bible)
			except: pass
			self.ui.bible_verses_list.setCurrentRow(int(search_res.verse) - 1)
		except Exception as error:
			pass


	def get_songs_from_songbook(self):
		try: self.ui.list_songs.itemSelectionChanged.disconnect(self.get_words)
		except: pass

		try: self.ui.list_words.itemSelectionChanged.disconnect(self.show_song)
		except: pass

		try:
			if self.ui.available_songbooks_element.currentText():
				current_songbook = self.ui.available_songbooks_element.currentText()
				self.connection = sqlite3.connect(f'Songbooks/{self.songbooks[current_songbook]["filename"]}')
				self.cursor = self.connection.cursor()
				song_names = self.cursor.execute("SELECT id, title FROM Songs").fetchall()

				self.ui.list_songs.clear()
				self.ui.list_words.clear()
				for i in song_names:
					self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

				self.ui.list_songs.itemSelectionChanged.connect(self.get_words)
				self.ui.list_words.itemSelectionChanged.connect(self.show_song)
		except Exception as e:
			print(e)


	def get_song(self, song_number):
		filename = self.songbooks[self.ui.available_songbooks_element.currentText()]["filename"]
		db = sqlite3.connect(f"Songbooks/{filename}")
		sql = db.cursor()
		song = sql.execute(f"SELECT * FROM Songs WHERE id='{song_number}'").fetchall()
		number = song[0][0]
		title = song[0][1]
		song_text = song[0][2]

		return Song(number, title, song_text)


	def get_words(self):
		try:
			self.ui.list_songs.itemSelectionChanged.disconnect(self.get_words)
		except:
			pass
		
		self.ui.list_words.itemSelectionChanged.disconnect(self.show_song)

		song_number = int(self.ui.list_songs.currentItem().text().split()[0])
		self.song = self.get_song(song_number)
		song_text = json.loads(self.song.song_text)
		song_couplets = song_text["Couplets"]
		song_chorus = song_text["Chorus"]
		song_bridges = song_text["Bridges"]

		self.ui.list_words.clear()

		song_parts = []

		if self.anyStreamMode:
			# Build song_parts for stream mode with a chorus after each couplet
			for couplet in song_couplets:
				song_parts.append(couplet)
				if song_chorus: 
					song_parts.append(song_chorus)
			for b in song_bridges:
				song_parts.insert(b["index"], b["text"])

			self.song_lines = [
				SongLine(line, song_parts[part], part) 
				for part in range(len(song_parts)) 
				for line in song_parts[part].split("\n")
			]

			for line in self.song_lines:
				line_custom_item = CustomItem(line.text, "part")
				line_item = SongItem(line.text, "part")
				line_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
				line_item.setSizeHint(line_custom_item.sizeHint())

				self.ui.list_words.addItem(line_item)
				self.ui.list_words.setItemWidget(line_item, line_custom_item)

		else:
			# Add couplets and chorus after each one in non-stream mode
			for couplet in song_couplets:
				self.add_song_item(couplet, "couplet")
				if song_chorus:
					self.add_song_item(song_chorus, "chorus")

			for b in song_bridges:
				self.add_song_item(b["text"], "bridge", b["index"])

		self.ui.list_words.setCurrentRow(0)

		self.ui.list_words.itemSelectionChanged.connect(self.show_song)
		self.ui.list_songs.itemSelectionChanged.connect(self.get_words)

	def add_song_item(self, text, item_type, index=None):
		custom_item = CustomItem(text, item_type)
		item = SongItem(text, item_type)
		item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
		item.setSizeHint(custom_item.sizeHint())

		if index is not None:
			self.ui.list_words.insertItem(index, item)
		else:
			self.ui.list_words.addItem(item)
		
		self.ui.list_words.setItemWidget(item, custom_item)


	def search_song(self):
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

		req = self.ui.song_search.text().strip()
		if req.isdigit():
			req = int(req)
			res = self.cursor.execute(f"SELECT * FROM Songs WHERE id={req}").fetchall()
		else:
			for s in songs:
				song_text_json = json.loads(s[2])
				song_text = ""
				for c in song_text_json["Couplets"]:
					song_text += c + "\n\n"
				song_text += song_text_json["Chorus"]
				if checkIn(song_text, req):
					res.append(s)

		self.ui.list_songs.clear()
		for i in res:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

		if not req: 
			if self.last_shown_song:
				self.ui.list_songs.setCurrentRow(self.last_shown_song.number - 1)
			elif self.song: 
				self.ui.list_songs.setCurrentRow(self.song.number - 1)
		else:
			try:
				self.ui.list_songs.setCurrentRow(0)
			except:
				pass


	def closeEvent(self, event):
		self.close_window()


	def show_song(self):
		try:
			self.screens[1]
		except:
			self.open_window()

		self.lastShown = "song"

		song_number = int(self.ui.list_songs.currentItem().text().split()[0])
		self.last_shown_song = self.get_song(song_number)

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

				background = settings[screen]["default_mode_settings"]["background"]
				self.screens[s].setStyleSheet("#WordsWindow { background: %s; }" % (background))

				font_size = settings[screen]["default_mode_settings"]["font_size"]

				label_width = screen_size.width() - settings[screen]["default_mode_settings"]["song_margins"]["h"]
				label_height = screen_size.height() - settings[screen]["default_mode_settings"]["song_margins"]["v"]

				# Set label to center
				label_center_x = label_width / 2
				label_center_y = label_height / 2
				screen_center_x = screen_size.width() / 2
				screen_center_y = screen_size.height() / 2
				self.screens[s].label.setGeometry(
					int(screen_center_x - label_center_x),
					int(screen_center_y - label_center_y),
					int(label_width),
					int(label_height)
				)
				self.screens[s].setShadow()
				# Set fit font
				self.screens[s].label.ownWordWrap(font_size)


	def show_bible(self):
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

				info_position = settings[screen]["stream_mode_settings"]["info_position"]
				self.screens[s].label_info.move(int(info_position["x"]), int(info_position["y"]))
				font_size = settings[screen]["stream_mode_settings"]["font_size_info"]
				f = QFont("Arial", font_size)
				f.setItalic(True)
				f.setBold(True)
				self.screens[s].label_info.setFont(f)
				self.screens[s].label_info.adjustSize()

			elif settings[screen]["show_words"] and not settings[screen]["stream_mode"]:
				self.screens[s].label.setText(self.ui.bible_verses_list.currentItem().text())

				background = settings[screen]["default_mode_settings"]["background"]
				self.screens[s].setStyleSheet("#WordsWindow { background: %s; }" % (background))

				font_size = settings[screen]["default_mode_settings"]["font_size"]
				f = QFont("Arial", font_size)
				f.setBold(True)
				self.screens[s].label.setFont(f)

				label_width = screen_size.width() - settings[screen]["default_mode_settings"]["bible_margins"]["h"]
				label_height = screen_size.height() - settings[screen]["default_mode_settings"]["bible_margins"]["v"]

				# Set label to center
				label_center_x = label_width / 2
				label_center_y = label_height / 2
				screen_center_x = screen_size.width() / 2
				screen_center_y = screen_size.height() / 2
				self.screens[s].label.setGeometry(
					int(screen_center_x - label_center_x),
					int(screen_center_y - label_center_y),
					int(label_width),
					int(label_height)
				)
				self.screens[s].setShadow()
				# Set fit font
				self.screens[s].label.ownWordWrap(font_size)

				bible_place = self.list_to_bible_place(self.bible_place)
				self.screens[s].label_info.setText(bible_place)

				info_position = settings[screen]["default_mode_settings"]["info_position"]
				self.screens[s].label_info.move(info_position["x"], info_position["y"])
				font_size = settings[screen]["default_mode_settings"]["font_size_info"]
				f = QFont("Arial", font_size)
				f.setItalic(True)
				self.screens[s].label_info.setFont(f)
				self.screens[s].label_info.adjustSize()


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

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(count_of_screens):
			self.screens.append(WordsWindow(i))


	def close_window(self, number=None):
		if not number:
			for s in self.screens:
				try: s.close()
				except: pass

			try: self.addsong.close()
			except: pass

			try: self.add_songbook_window.close()
			except: pass
		elif number:
			try: self.screens[int(number)].close()
			except Exception as error: print(error)


	def hide_text(self):
		try:
			self.screens[1]
		except:
			return

		self.lastShown = None

		for s in self.screens:
			if s.isShowing:
				s.label.setText("")
				if s.label_info.text().strip(): s.label_info.setText("")
				if not s.stream_mode(): 
					s.setStyleSheet("#WordsWindow { background: %s; }" % (s.passive_background()))


	def set_values(self):
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
		self.ui.font_size_input.setValue(settings[screen]["default_mode_settings"]["font_size"])
		self.ui.text_color_input.setText(settings[screen]["default_mode_settings"]["text_color"])
		self.ui.background_color_input.setText(settings[screen]["default_mode_settings"]["background"])
		self.ui.passive_background_color_input.setText(settings[screen]["default_mode_settings"]["passive_background"])
		self.ui.shadow_checkbox.setChecked(settings[screen]["default_mode_settings"]["shadow"])
		self.ui.shadow_blur_radius_input.setValue(settings[screen]["default_mode_settings"]["shadow_blur_radius"])
		self.ui.shadow_offset_x_input.setValue(settings[screen]["default_mode_settings"]["shadow_offset"]["x"])
		self.ui.shadow_offset_y_input.setValue(settings[screen]["default_mode_settings"]["shadow_offset"]["y"])

		self.ui.checkbox_stream_mode.setChecked(settings[screen]["stream_mode"])
		self.ui.font_size_input_stream.setValue(settings[screen]["stream_mode_settings"]["font_size"])
		self.ui.text_color_input_stream.setText(settings[screen]["stream_mode_settings"]["text_color"])
		self.ui.shadow_checkbox_stream.setChecked(settings[screen]["stream_mode_settings"]["shadow"])
		self.ui.shadow_blur_radius_input_stream.setValue(settings[screen]["stream_mode_settings"]["shadow_blur_radius"])
		self.ui.shadow_offset_x_input_stream.setValue(settings[screen]["stream_mode_settings"]["shadow_offset"]["x"])
		self.ui.shadow_offset_y_input_stream.setValue(settings[screen]["stream_mode_settings"]["shadow_offset"]["y"])

		
	def set_settings(self):
		screen_number = self.ui.screensCB.currentText()
		screen = "screen_" + str(screen_number)

		show_words = bool(self.ui.checkbox_show_words.checkState())
		text_color = self.ui.text_color_input.text()
		background = self.ui.background_color_input.text()
		passive_background = self.ui.passive_background_color_input.text()
		font_size = self.ui.font_size_input.value()
		shadow = bool(self.ui.shadow_checkbox.checkState())
		shadow_blur_radius = self.ui.shadow_blur_radius_input.value()
		shadow_offset_x = self.ui.shadow_offset_x_input.value()
		shadow_offset_y = self.ui.shadow_offset_y_input.value()

		stream_mode = bool(self.ui.checkbox_stream_mode.checkState())
		text_color_stream = self.ui.text_color_input_stream.text()
		font_size_stream = self.ui.font_size_input_stream.value()
		shadow_stream = bool(self.ui.shadow_checkbox_stream.checkState())
		shadow_blur_radius_stream = self.ui.shadow_blur_radius_input_stream.value()
		shadow_offset_x_stream = self.ui.shadow_offset_x_input_stream.value()
		shadow_offset_y_stream = self.ui.shadow_offset_y_input_stream.value()
		
		# Write setting to json file
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		try:
			settings[screen]["show_words"]
		except:
			return

		settings[screen]["show_words"] = show_words
		settings[screen]["default_mode_settings"]["text_color"] = text_color
		settings[screen]["default_mode_settings"]["background"] = background
		settings[screen]["default_mode_settings"]["passive_background"] = passive_background
		settings[screen]["default_mode_settings"]["font_size"] = font_size
		settings[screen]["default_mode_settings"]["shadow"] = shadow
		settings[screen]["default_mode_settings"]["shadow_blur_radius"] = shadow_blur_radius
		settings[screen]["default_mode_settings"]["shadow_offset"]["x"] = shadow_offset_x
		settings[screen]["default_mode_settings"]["shadow_offset"]["y"] = shadow_offset_y

		if settings[screen]["stream_mode"] != stream_mode: self.streamModeChanged = True
		else: self.streamModeChanged = False

		settings[screen]["stream_mode"] = stream_mode
		settings[screen]["stream_mode_settings"]["text_color"] = text_color_stream
		settings[screen]["stream_mode_settings"]["font_size"] = font_size_stream
		settings[screen]["stream_mode_settings"]["shadow"] = shadow_stream
		settings[screen]["stream_mode_settings"]["shadow_blur_radius"] = shadow_blur_radius_stream
		settings[screen]["stream_mode_settings"]["shadow_offset"]["x"] = shadow_offset_x_stream
		settings[screen]["stream_mode_settings"]["shadow_offset"]["y"] = shadow_offset_y_stream

		# Write to file
		with open("screens_settings.json", "w") as jsonfile:
			jsonfile.write(json.dumps(settings, indent=4))

		# Apply settings
		self.anyStreamMode = self.check_stream_mode()
		if not self.streamModeChanged:
			if self.lastShown == "song":
				self.show_song()
			elif self.lastShown == "bible":
				self.show_bible()
		elif self.streamModeChanged:
			self.hide_text()
			if self.lastShown: self.get_words()
		
		self.apply_settings_for_screens()

		self.ui.list_words.itemSelectionChanged.disconnect(self.show_song)

		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		if settings[screen]["stream_mode"]:
			self.ui.settings_mode_tabs.setCurrentIndex(1)
		else:
			self.ui.settings_mode_tabs.setCurrentIndex(0)

		self.ui.list_words.itemSelectionChanged.connect(self.show_song)


	def apply_settings_for_screens(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		for i in range(len(self.screens)):
			screen = "screen_" + str(i)
			if not settings[screen]["show_words"]:
				try: 
					self.screens[i].close()
				except: pass

			if not self.screens[i].isShowing and settings[screen]["show_words"]:
				self.open_window()

			if settings[screen]["stream_mode"] and settings[screen]["show_words"]:
				background = settings[screen]["stream_mode_settings"]["background"]
				styles = "#WordsWindow { background: %s; }" % (background)
				text_color = settings[screen]["stream_mode_settings"]["text_color"]
				
				self.screens[i].setStyleSheet(styles)
				self.screens[i].label.setStyleSheet(f"color: {text_color};")

				if settings[screen]["stream_mode_settings"]["shadow"]: self.screens[i].setShadow()
			
			elif not settings[screen]["stream_mode"] and settings[screen]["show_words"]:
				text_color = settings[screen]["default_mode_settings"]["text_color"]
				if self.lastShown:
					background = settings[screen]["default_mode_settings"]["background"]
					styles = "#WordsWindow { background: %s; }" % (background)
					self.screens[i].setStyleSheet(styles)
				else:
					passive_background = settings[screen]["default_mode_settings"]["passive_background"]
					styles = "#WordsWindow { background: %s; }" % (passive_background)
					self.screens[i].setStyleSheet(styles)
				
				self.screens[i].label.setStyleSheet(f"color: {text_color};")

				if settings[screen]["default_mode_settings"]["shadow"]: self.screens[i].setShadow()



if __name__ == "__main__":
	app = QApplication([])
	application = LyricVerse()
	application.show()

	sys.exit(app.exec())



# My updater is gonna mess up all the settings and songbooks (Maybe a good solution would be to download just the exe file instead of the whole app archive)
