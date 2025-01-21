from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from smart_label import SmartLabel

import json


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
			if settings[screen]["stream_mode"]: background = "rgb(0, 255, 0)"
			else: background = self.passive_background()
			self.setObjectName("WordsWindow")
			styles = """#WordsWindow {
				background: %s;
			}
			""" % (background)
			self.setStyleSheet(styles)

			self.label = SmartLabel(self)
			if settings[screen]["stream_mode"]:
				mode = "stream_mode_settings"
			else:
				mode = "default_mode_settings"

			font_size = settings[screen][mode]["font_size"]
			text_color = settings[screen][mode]["text_color"]
			font_size_info = settings[screen][mode]["font_size_info"]
			text_color_info = settings[screen][mode]["text_color_info"]

			f = QFont("Arial", font_size)
			f.setBold(True)
			self.label.setStyleSheet(f"color: {text_color}")
			self.label.setFont(f)
			self.label.setText("")
			self.label.setTextFormat(Qt.AutoText)
			self.label.setAlignment(Qt.AlignCenter)

			self.label_info = QLabel(self)
			self.label_info.setGeometry(QRect(10, 10, 400, 400))
			f = QFont("Arial", font_size_info)
			f.setItalic(True)
			self.label_info.setFont(f)
			self.label_info.setStyleSheet(f"color: {text_color_info}")

			self.setShadow()

			monitor = QDesktopWidget().screenGeometry(self.screen_number)
			self.move(monitor.left(), monitor.top())

			self.showFullScreen()
			self.isShowing = True


	def stream_mode(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)
		screen = "screen_" + str(self.screen_number)
		if settings[screen]["stream_mode"]: return True
		else: return False


	def passive_background(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)
		screen = "screen_" + str(self.screen_number)
		return settings[screen]["default_mode_settings"]["passive_background"]


	def setShadow(self):
		with open("screens_settings.json", "r") as jsonfile:
			settings = json.load(jsonfile)

		screen = "screen_" + str(self.screen_number)
		if settings[screen]["stream_mode"]:
			mode = "stream_mode_settings"
		else:
			mode = "default_mode_settings"

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

	
	def closeEvent(self, event):
		self.isShowing = False