import json

# from text import text

class Song:
	def __init__(self, number, title, song_text):
		self.number = number
		self.title = title
		self.song_text = song_text

		song_text_lines = self.song_text.split("\n")
		self.song_list = []
		part_of_song = ""
		for t in range(0, len(song_text_lines)):
			if "куплет" in song_text_lines[t].lower() or "приспів" in song_text_lines[t].lower() or "припев" in song_text_lines[t].lower():
				if t != 0:
					self.song_list.append(part_of_song)
					part_of_song = ""
			part_of_song += song_text_lines[t] + "\n"
		self.song_list.append(part_of_song.strip())


	def __getCouplets(self):
		couplets = []
		for c in self.song_list:
			c_0 = c.split("\n")[0].lower()
			if "куплет" in c_0:
				c = c.split("\n")[1:]
				c = "\n".join(c)
				couplets.append(c.strip())

		return couplets

	def __getChour(self):
		chour = ""
		for c in self.song_list:
			c_0 = c.split("\n")[0].lower()
			if "приспів" in c_0 or "припев" in c_0:
				c = c.split("\n")[1:]
				c = "\n".join(c)
				chour = c.strip()

		return chour

	def reformat_text_to_json(self, repeat_chour=True):
		couplets = self.__getCouplets()
		chour = self.__getChour()
		Song = {
			"Couplets": couplets,
			"Chour": chour,
			"repeat_chour": repeat_chour
		}
		song_json = json.dumps(Song, indent=4)
		self.song_text = song_json


# song = Song(44, "hello", text)
# print(song.song_text)
# song.reformat_text_to_json()
# print(song.song_text)

# song = json.loads(song.song_text)
# print(song["Chour"])