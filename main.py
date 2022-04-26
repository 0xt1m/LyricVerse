from design import Ui_MainWindow
# from words_window import Ui_WordsWindow

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidgetItem, QShortcut, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QTransform, QKeySequence, QFont, QFontMetrics

from configparser import ConfigParser
from mybible_handler import Mybible

import sqlite3

import sys



class Song:
	def __init__(self, song_title):
		db = sqlite3.connect("Songs.db")
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
			
			self.label.setStyleSheet(f"""
				color: {config[f'screen_{self.screen_number}']['text_color']};\n
			""")
			self.label.setText("")
			self.label.setTextFormat(QtCore.Qt.AutoText)
			self.label.setAlignment(QtCore.Qt.AlignCenter)
			self.label.setScaledContents(True)

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
		# self.ui.btn_showWindow.clicked.connect(self.open_window)
		# self.ui.btn_closeWindow.clicked.connect(self.close_window)
		self.ui.song_search.textChanged.connect(self.searchSong)
		self.ui.list_songs.itemSelectionChanged.connect(self.getWords)
		self.ui.list_words.itemSelectionChanged.connect(self.showWords)
		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(self.hide_text)
		self.ui.screensCB.currentTextChanged.connect(self.set_settings_from_screen)
		self.ui.btn_save.clicked.connect(self.change_settings_for_screen)
		self.ui.btn_save.clicked.connect(self.set_settings_for_screen)

		self.ui.list_words.setSpacing(5)

		# self.ui.list_songs.itemPressed.connect(self.getWords)
		# self.ui.list_words.itemPressed.connect(self.showWords)

		con = sqlite3.connect("Songs.db")
		cur = con.cursor()
		song_names = cur.execute("SELECT id, title FROM Songs").fetchall()

		for i in song_names:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(0, count_of_screens):
			self.ui.screensCB.addItem(str(i))

		self.anyStreamMode = False
		self.set_settings_for_screen()
		self.open_window()

	def closeEvent(self, event):
		self.close_window()


	def searchSong(self):
		try:
			self.ui.list_songs.setCurrentRow(0)
		except:
			pass
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

		db = sqlite3.connect("Songs.db")
		sql = db.cursor()

		songs = sql.execute("SELECT * FROM Songs").fetchall()
		res = []
		
		req = self.ui.song_search.text()
		if req.isdigit():
			req = int(req)
			res = sql.execute(f"SELECT * FROM Songs WHERE id={req}").fetchall()
		else:
			for song in songs: 
				if checkIn(song[2], req):
					res.append(song)
		
		self.ui.list_songs.clear()
		for i in res:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])


	def getWords(self):
		text_l = self.ui.list_songs.currentItem().text().split()
		text_l.pop(0)
		
		song_title = ""
		for t in text_l:
			song_title += t + " "
		song_title = song_title.strip()
		
		song = Song(song_title)
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

		self.hide_text()


	def showWords(self):
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
			
			font_size = int(config.get(f"screen_{s}", "font_size"))
			f = QFont("Arial", font_size)
			f.setBold(True)
			self.screens[s].label.setFont(f)

			if self.screens[s].isShowing == False:
				self.open_window()
			if self.anyStreamMode:
				try:
					partIndex = int(self.song_list_lines[self.ui.list_words.currentRow()].split().pop())
					if config.get(f"screen_{s}", "stream_mode") == "1":
						line = self.ui.list_words.currentItem().text()
						if config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(line)
					else:
						part = self.song_list_parts[partIndex]
						if config.get(f"screen_{s}", "show_words") == "1":
							self.screens[s].label.setText(part)
				except:
					pass
			else:
				try:
					part = self.ui.list_words.currentItem().text()
					if config.get(f"screen_{s}", "show_words") == "1":
						self.screens[s].label.setText(part)
				except:
					pass

			active_text = self.screens[s].label.text()

			self.screens[s].label.adjustSize()
			# self.screens[s].label.setScaledContents(True)

			screen_size = QDesktopWidget().availableGeometry(s)
			text_size = self.screens[s].label.size()
			
			while text_size.width() > screen_size.width() - 10 or text_size.height() > screen_size.height() - 10:
				font_size -= 1
				nf = QFont("Arial", font_size)
				nf.setBold(True)
				self.screens[s].label.setFont(nf)
				if config.get(f"screen_{s}", "show_words") == "1":
					self.screens[s].label.setText(active_text.strip())
				if config.get(f"screen_{s}", "stream_mode") == "0":
					self.screens[s].label.setWordWrap(True)
				self.screens[s].label.adjustSize()

				screen_size = QDesktopWidget().availableGeometry(s)
				text_size = self.screens[s].label.size()

			screen_center_x = screen_size.width() / 2
			screen_center_y = screen_size.height() / 2
			text_center_x = text_size.width() / 2
			text_center_y = text_size.height() / 2

			if config.get(f"screen_{s}", "stream_mode") == "0":
				self.screens[s].label.move(screen_center_x - text_center_x, screen_center_y - text_center_y)
			
			if config.get(f"screen_{s}", "stream_mode") == "1":
				self.screens[s].label.move(screen_center_x - text_center_x, screen_size.height() - int(config.get(f"screen_{s}", "margin_bottom")))

			# self.screens[s].label.setScaledContents(True)


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
	

	def moveElement(self):
		self.ui.label_move.move(self.ui.h_slider.value(), self.ui.v_slider.value())


	def setFZ(self):
		self.ui.label_move.setStyleSheet(f"font-size: {self.ui.fz_slider.value()}px")


	def print_on(self):
		print("blablabla")

	
	def get_screens(self):
		# screenres = QRect()
		screens = QDesktopWidget().screenCount()
		print(screens)

	
	def sel_all(self):
		self.ui.textEdit.select_all()


if __name__ == "__main__":
	app = QtWidgets.QApplication([]) #QtWidgets.QApplication([])
	application = ScreenShower()
	application.show()

	sys.exit(app.exec())







