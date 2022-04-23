from design import Ui_MainWindow
# from words_window import Ui_WordsWindow

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidgetItem, QShortcut, QWidget
from PyQt5.QtGui import QTransform, QKeySequence, QFont, QFontMetrics

from configparser import ConfigParser

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
				couplets.append(c.strip())

		return couplets

	def getChour(self):
		chour = ""
		for c in self.song_list:
			c_0 = c.split("\n")[0].lower()
			if "приспів" in c_0 or "приспів:" in c_0:
				chour = c.strip()

		return chour


class WordsWindow(QMainWindow):
	def __init__(self, screen_number):
		super().__init__()

		config = ConfigParser()
		config.read("screens_config.ini")
		
		self.setStyleSheet(f"""
 			background-color: {config[f"screen_{screen_number}"]["background_color"]};
			color: {config[f"screen_{screen_number}"]["text_color"]};
		""")

		self.main_text = QtWidgets.QLabel(self)
		self.main_text.setText("blablabla")
		self.main_text.move(100, 100)
		self.main_text.adjustSize()

		self.label = QtWidgets.QLabel(self)

		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(ScreenShower.hide_text)


class WordsWindowStream(QMainWindow):
	def __init__(self):
		pass



class ScreenShower(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()

	def init_ui(self):
		self.ui.btn_showWindow.clicked.connect(self.open_window)
		self.ui.btn_closeWindow.clicked.connect(self.close_window)
		self.ui.search_input.textChanged.connect(self.searchSong)
		self.ui.list_songs.itemSelectionChanged.connect(self.getWords)
		self.ui.list_words.itemSelectionChanged.connect(self.showWords)
		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(self.hide_text)
		self.ui.screensCB.currentTextChanged.connect(self.set_settings_from_screen)
		self.ui.btn_set.clicked.connect(self.change_settings_for_screen)
		self.ui.btn_set.clicked.connect(self.set_settings_for_screen)

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

	def closeEvent(self, event):
		self.close_window()


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

		db = sqlite3.connect("Songs.db")
		sql = db.cursor()

		songs = sql.execute("SELECT * FROM Songs").fetchall()
		res = []
		
		req = self.ui.search_input.text()
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
		song_chour = ""
		song_chour = song.getChour()
		
		self.ui.list_words.clear()
		for i in song_couplets:
			self.ui.list_words.addItem(i)
			if song_chour != "":
				self.ui.list_words.addItem(song_chour)

		self.hide_text()


	def showWords(self):
		try:
			self.screen1
		except:
			self.open_window()

		def rmCount(text):
			res = ""
			text_l = text.split("\n")
			for i in range(len(text_l)):
				try:
					part = text_l[i].lower()
					if "куплет" in part or "куплет:" in part or "приспів" in part or "приспів:" in part:
						text_l.pop(i)
				except:
					pass

			for i in text_l:
				res += i + "\n"

			return res

		active_text = rmCount(self.ui.list_words.currentItem().text())
		if not self.screen1.isShowing:
			self.open_window()
			self.screen1.isShowing = True
		

		config = ConfigParser()
		config.read("screens_config.ini")
		
		f = QFont("Arial", int(config["screen_1"]["font_size"]))
		self.screen1.ui.label.setFont(f)
		self.screen1.ui.label.setText(active_text.strip())
		self.screen1.ui.label.setWordWrap(True)
		self.screen1.ui.label.adjustSize()
		
		screen1_size = QDesktopWidget().availableGeometry(1)
		text_size = self.screen1.ui.label.size()

		font_size = int(config["screen_1"]["font_size"])
		
		while text_size.width() > screen1_size.width() - 10 or text_size.height() > screen1_size.height() - 10:
			font_size -= 1
			nf = QFont("Arial", font_size)
			self.screen1.ui.label.setFont(nf)
			self.screen1.ui.label.setText(active_text.strip())
			self.screen1.ui.label.setWordWrap(True)
			self.screen1.ui.label.adjustSize()

			screen1_size = QDesktopWidget().availableGeometry(1)
			text_size = self.screen1.ui.label.size()

		screen1_center_x = screen1_size.width() / 2
		screen1_center_y = screen1_size.height() / 2
		text_center_x = text_size.width() / 2
		text_center_y = text_size.height() / 2

		self.screen1.ui.label.move(screen1_center_x - text_center_x, screen1_center_y - text_center_y)


	def open_window(self):
		config = ConfigParser()
		config.read("screens_config.ini")
		# print(config["screen_1"]["font_size"])
		# self.count_of_monitors = 2
		# self.window = []

		self.screens = []

		count_of_screens = QDesktopWidget().screenCount()
		for i in range(count_of_screens):
			show_words = bool(int(config.get(f"screen_{i}", "show_words")))
			stream_mode = bool(int(config.get(f"screen_{i}", "stream_mode")))
			if show_words and stream_mode:
				self.screens.append(None)
			elif show_words:
				self.screens.append(WordsWindow(i))

				screen_geometry = QDesktopWidget().availableGeometry(i)
				monitor = QDesktopWidget().screenGeometry(i)
				self.screens[i].move(monitor.left(), monitor.top())

				self.screens[i].showFullScreen()
			else:
				self.screens.append(None)








		# self.screen1 = QtWidgets.QMainWindow()
		# self.screen1.ui = WordsWindow()
		# self.screen1.ui.setupUi(self.screen1)
		# self.screen1.quitSc = QShortcut(QKeySequence('Esc'), self.screen1)
		# self.screen1.quitSc.activated.connect(self.hide_text)

		# self.screen1.isShowing = True

		# self.screen1.setStyleSheet(f"""
		# 		background-color: {config["screen_1"]["background_color"]};
		# 		color: {config["screen_1"]["text_color"]};
		# 	""")

		# screen1_geometry = QDesktopWidget().availableGeometry(1)
		# monitor = QDesktopWidget().screenGeometry(1)
		# print(monitor.left())
		# self.screen1.ui.label.setGeometry(0, 0, screen1_geometry.width(), screen1_geometry.height())
		
		# self.screen1.setWindowFlags(Qt.FramelessWindowHint)
		# self.screen1.move(monitor.left(), monitor.top())
		# self.screen1.show()
		# self.screen1.showFullScreen()
		# try:
			# self.showWords()
		# except:
			# pass


		# m = self.count_of_monitors - 1
		# i = 0
		# while m >= 0:
		# 	screen_geometry = QDesktopWidget().availableGeometry(m)
		# 	print(screen_geometry)
			
		# 	self.window.append(QtWidgets.QMainWindow())
		# 	self.window[i].ui = Ui_OtherWindow()
		# 	self.window[i].ui.setupUi(self.window[i])
			
		# 	monitor = QDesktopWidget().screenGeometry(m)
		# 	self.window[i].ui.label.setGeometry(abs(screen_geometry.x()), 0, screen_geometry.width(), screen_geometry.height())
		# 	# self.window.setWindowFlags(Qt.FramelessWindowHint)
		# 	self.window[i].move(monitor.left(), monitor.top())
		# 	self.window[i].showFullScreen()
		# 	m -= 1
		# 	i += 1

	
	def close_window(self):
		try:
			self.screen1.isShowing
		except:
			return
		if self.screen1.isShowing:
			self.screen1.close()	
			self.screen1.isShowing = False
		
		# if self.window:
		# 	for w in range(len(self.window)):
		# 		self.window[w].close()


	def hide_text(self):
		try:
			self.screen1.isShowing
		except:
			return
		if self.screen1.isShowing:
			self.screen1.ui.label.setText("")


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
		stream_mode = bool(int(config.get(f"screen_{screen_number}", "stream_mode")))

		if show_words:
			self.open_window()
		else:
			self.close_window()





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







