from design import Ui_MainWindow
from other_window import Ui_OtherWindow

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidgetItem, QShortcut
from PyQt5.QtGui import QTransform, QKeySequence

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
		# couplets = []
		# chorus = ""
		# couplet = ""

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



class ScreenShower(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.init_ui()

	def init_ui(self):
		self.ui.btn_showWindow.clicked.connect(self.open_window)
		self.ui.btn_closeWindow.clicked.connect(self.close_window)
		self.ui.btn_showText.clicked.connect(self.show_text)
		# self.ui.btn_up.clicked.connect(self.add_words)
		self.ui.h_slider.valueChanged.connect(self.moveElement)
		self.ui.v_slider.valueChanged.connect(self.moveElement)
		self.ui.fz_slider.valueChanged.connect(self.setFZ)
		self.ui.search_input.textChanged.connect(self.searchSong)
		self.ui.list_songs.itemPressed.connect(self.getWords)
		self.ui.list_songs.itemSelectionChanged.connect(self.getWords)
		self.ui.list_words.itemPressed.connect(self.showWords)
		self.ui.list_words.itemSelectionChanged.connect(self.showWords)
		self.quitSc = QShortcut(QKeySequence('Esc'), self)
		self.quitSc.activated.connect(self.close_window)
		
		self.ui.label_move.move(self.ui.h_slider.value(), self.ui.v_slider.value())

		con = sqlite3.connect("Songs.db")
		cur = con.cursor()
		song_names = cur.execute("SELECT id, title FROM Songs").fetchall()

		for i in song_names:
			self.ui.list_songs.addItem(str(i[0]) + " " + i[1])

	
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
		self.screen1.ui.label.setText(active_text)


	def open_window(self):
		config = ConfigParser()
		config.read("screens_config.ini")
		# print(config["screen_1"]["font_size"])
		# self.count_of_monitors = 2
		# self.window = []

		self.screen1 = QtWidgets.QMainWindow()
		self.screen1.ui = Ui_OtherWindow()
		self.screen1.ui.setupUi(self.screen1)
		self.screen1.quitSc = QShortcut(QKeySequence('Esc'), self.screen1)
		self.screen1.quitSc.activated.connect(self.close_window)

		self.screen1.isShowing = True

		self.screen1.setStyleSheet(f"""
				background-color: {config["screen_1"]["background_color"]};
				color: {config["screen_1"]["text_color"]};
				font-size: {config["screen_1"]["font_size"]}px;
			""")

		screen1_geometry = QDesktopWidget().availableGeometry(1)
		monitor = QDesktopWidget().screenGeometry(1)
		# print(monitor.left())
		self.screen1.ui.label.setGeometry(0, 0, screen1_geometry.width(), screen1_geometry.height())
		# self.screen1.setWindowFlags(Qt.FramelessWindowHint)
		self.screen1.move(monitor.left(), monitor.top())
		self.screen1.showFullScreen()
		try:
			self.showWords()
		except:
			pass

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
		if self.screen1.isShowing:
			self.screen1.close()
			self.screen1.isShowing = False
		# if self.window:
		# 	for w in range(len(self.window)):
		# 		self.window[w].close()

	
	def show_text(self):
		text = ""
		try:
			text = self.ui.list_words.currentItem().text().replace("Куплет:", "").replace("Приспів:", "").strip()
		except:
			text = ""
		try:
			for w in self.window:
				w.ui.label.move(w.width() / 2, w.height / 2)
				w.ui.label.setText(text)
		except:
			return 0


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
	application.close_window()







