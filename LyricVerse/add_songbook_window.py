import sqlite3, json, shutil

from song import Song

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QFont


class AddSongbookWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.resize(420, 500)
		self.setWindowTitle("Додати пісенник")

		self.file = FileLabel(self)
		self.file.mousePressEvent = self.browseFiles

		self.label = QLabel(self)
		self.label.setText("Введіть назву пісенника:")
		self.label.adjustSize()
		self.label.move(10, 10)

		self.songbook_title_input = QLineEdit(self)
		self.songbook_title_input.setPlaceholderText("Євангельські пісні")
		self.songbook_title_input.setGeometry(10, 30, 200, 20)

		self.add_btn = QPushButton("Зберегти", self)
		self.add_btn.setGeometry(10, 465, 400, 30)
		self.add_btn.clicked.connect(self.add_songbook)


	def browseFiles(self, event):
		font = QFont("Arial", 12)

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Помилка")

		file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
		file = QFileInfo(file_name[0])
		if file.suffix() == "db":
			self.selected_file_path = file.absoluteFilePath()
			self.file.setText(file.fileName())
			self.file.setFont(font)
		else:
			msg.setText("Неможливо розпізнати формат файлу")	
			msg.exec_()


	def add_songbook(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Warning)
		msg.setWindowTitle("Помилка")
		
		if self.songbook_title_input.text().strip() == "":
			msg.setText("Не може бути пісенник без назви!")	
			msg.exec_()
		elif self.file.text() == "Файл з піснями":
			filename = self.songbook_title_input.text().strip() + ".db"
			connection = sqlite3.connect("Songbooks/" + filename)
			cursor = connection.cursor()

			try:
				cursor.execute("DROP TABLE Songs;")
			except:
				pass
			cursor.execute('CREATE TABLE Songs (id INTEGER NOT NULL, title TEXT NOT NULL, song_text TEXT NOT NULL, PRIMARY KEY("id" AUTOINCREMENT));')

			connection.commit()
			add_songbook_to_json(filename, self.songbook_title_input.text().strip())
			self.close()
		else:
			filename = self.file.text()
			songbook_name = self.songbook_title_input.text().strip()

			print(self.selected_file_path)

			shutil.copy(self.selected_file_path, f"./Songbooks/{filename}")
			add_songbook_to_json(filename, songbook_name)

			self.close()


class FileLabel(QLabel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAcceptDrops(True)
		self.resize(400, 400)
		self.move(10, 60)
		self.setText("Файл з піснями")
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
		msg.setWindowTitle("Помилка")
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()

			if len(event.mimeData().urls()) > 1:
				msg.setText("Можна перетягувати тільки один файл!")	
				msg.exec_()
			else:
				url = event.mimeData().urls()[0]
				if url.isLocalFile():
					file = QFileInfo(str(url.toLocalFile()))
					if file.suffix() == "sps":
						self.setText(file.fileName())
						self.setFont(font)
					else:
						msg.setText("Неможливо розпізнати формат файлу!")	
						msg.exec_()
				
		else:
			event.ignore()


def add_songbook_to_json(filename, title="Songbook"):
	title = title.replace(".db", "")
	with open("Songbooks/songbooks.json", "r") as jsonfile:
		songbooks = json.load(jsonfile)
	try:
		songbooks[title]["filename"] = filename
	except:
		songbooks.setdefault(title, {"filename": filename})
	
	with open("Songbooks/songbooks.json", "w") as jsonfile:
		json.dump(songbooks, jsonfile, indent=4)


def importSongsFromSP(filename, title):
	def remove_duplicates(songs):
		songs_len = len(songs)
		i = 0
		while i < songs_len:
			s = songs[i][0]
			j = i+1
			while j < songs_len:
				if songs[j][0] == songs[i][0]:
					songs.pop(j)
					songs_len -= 1
				j += 1
			i += 1
		return songs

	connection = sqlite3.connect("Songbooks/" + filename)
	cursor = connection.cursor()

	all_songs = cursor.execute("SELECT * FROM Songs").fetchall()

	connection = sqlite3.connect("Songbooks/" + filename.replace(".sps", ".db"))
	cursor = connection.cursor()

	# If database with the filename is already exists remove all records from there
	try:
		cursor.execute("DROP TABLE Songs;")
	except:
		pass
	cursor.execute('CREATE TABLE Songs (id INTEGER NOT NULL, title TEXT NOT NULL, song_text TEXT NOT NULL, PRIMARY KEY("id" AUTOINCREMENT));')

	# Remove duplicates from these songs
	all_songs = remove_duplicates(all_songs)

	# Add songs to new database
	for song in range(len(all_songs)):
		song = Song(all_songs[song][0], all_songs[song][1], all_songs[song][6])
		song.reformat_text_to_json()
		cursor.execute('INSERT INTO Songs (id, title, song_text) VALUES (?, ?, ?);', (song.number, song.title, song.song_text))

	connection.commit()
	add_songbook_to_json(filename.replace("sps", "db"), title)