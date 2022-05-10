import sqlite3
import json


# Function for add or change records in json songbooks
def addSongbookToJson(filename, title="Songbook"):
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
	# Function for remove duplication song numbers from songs
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

	# global filename

	# import all songs from softprojector
	connection = sqlite3.connect("Songbooks/" + filename)
	cursor = connection.cursor()

	all_songs = cursor.execute("SELECT * FROM Songs").fetchall()

	# Create new database for ScreenShower
	connection = sqlite3.connect("Songbooks/" + filename.replace(".sps", ".db"))
	cursor = connection.cursor()

	# If database with the filename is already exists remove all records from there
	try:
		cursor.execute("DROP TABLE Songs;")
	except:
		pass
	cursor.execute("CREATE TABLE Songs (id INTEGER NOT NULL, title TEXT NOT NULL, song_text TEXT NOT NULL);")

	# Remove duplicates from these songs
	all_songs = remove_duplicates(all_songs)

	# Append songs to new database
	for song in range(len(all_songs)):
		cursor.execute('INSERT INTO Songs (id, title, song_text) VALUES (?, ?, ?);', (all_songs[song][0], all_songs[song][1], all_songs[song][6]))

	connection.commit()
	addSongbookToJson(filename.replace("sps", "db"), title)
		

# importSongsFromSP("EvPisni.sps")







