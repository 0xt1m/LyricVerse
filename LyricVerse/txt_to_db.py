import json
import sqlite3

TXT_FILE = "p_s_ua.txt"

class Song:
    def __init__(self, title, couplets, chorus="", bridges=[]):
        self.title = title
        self.couplets = couplets
        self.chorus = chorus
        self.bridges = bridges


def is_song_title(line):
    parts = line.split()
    if parts[0][0].isdigit() and parts[0][-1] == ".":
        if parts[0].replace(".", "").isdigit():
            return True

    return False


def divide_songs(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    songs = []
    song = ""
    for line in lines:
        line = line.strip().replace('\ufeff', "")
        if line and is_song_title(line):
            song += "\n"
            if song.strip(): 
                songs.append(song.strip())
            
            song = ""
        song += line + "\n"

    songs.append(song)
    return songs


def parse_song(song_text):
    song_blocks = song_text.split("\n\n")
    
    title = song_blocks[0].split(".")[1].strip()
    couplets = []
    chorus = ""
    bridges = []

    for block in song_blocks:
        block_lines = block.split("\n")
        if block_lines[0] == "#Куплет":
            couplet = block.replace("#Куплет", "").strip()
            couplets.append(couplet)
        elif block_lines[0] == "#Припев":
            chorus = block.replace("#Припев", "").strip()

    return Song(title, couplets, chorus, bridges)


def song_to_json(song):
    song_data = {
        "Couplets": song.couplets,
        "Chorus": song.chorus,
        "Bridges": song.bridges
    }

    return json.dumps(song_data, indent=4)


# songs = divide_songs(TXT_FILE)

conn = sqlite3.connect("./Songbooks/ps_us.db")
cursor = conn.cursor()

# Create the Songs table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS Songs (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     song_text TEXT NOT NULL
# )
# """)

# for song in songs:
#     parsed = parse_song(song)
#     json_song = song_to_json(parsed)
#     cursor.execute(f"INSERT INTO Songs (title, song_text) VALUES (?, ?)", (parsed.title, json_song))

# Commit changes and close the connection
# conn.commit()
# print("Songs added successfully to the database!")
# conn.close()


cursor.execute("SELECT * FROM Songs")
rows = cursor.fetchall()[:2]
print(rows)

# Print the rows
for row in rows:
    print(f"ID: {row[0]}, Title: {row[1]}, Song Text: {row[2]}")

conn.close()

# ,
#     "\u041F\u0456\u0441\u043D\u0456 \u0421\u043F\u0430\u0441\u0435\u043D\u043D\u0438\u0445": {
#         "filename": "ps_us.db"
#     }