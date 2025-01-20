import json

# from text import text

class Song:
	def __init__(self, number, title, song_text):
		self.number = number
		self.title = title
		self.song_text = song_text

		# self.__setTextWrap()

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

	def reformat_text_to_json(self):
		couplets = self.__getCouplets()
		chour = self.__getChour()
		Song = {
			"Couplets": couplets,
			"Chour": chour,
			"Bridges": []
		}
		song_json = json.dumps(Song, indent=4)
		self.song_text = song_json


	def __setTextWrap(self):
		self.song_text = self.song_text.replace("\n", " ")
		text_list = list(self.song_text)
		lines_list = []
		line = ""
		i = 0
		counter = 0
		while i < len(text_list):
			if counter == 50:
				copy_i = i
				copy_line = line
				while text_list[i] != " ": 
					if i == 0:
						i = copy_i
						line = copy_line + "-\n"
						break
					i -= 1
					line = line[:-1]
					
				lines_list.append(line.strip())
				counter = 0
				line = ""
			
			if text_list[i] == " " and text_list[i - 1] == " ": i += 1
			else:
				line += text_list[i]
				i += 1
				counter += 1
		lines_list.append(line.strip())
		# self.song_text = "\n".join(lines_list)



# song = Song(44, "hello", text)
# print(song.song_text)
# song.reformat_text_to_json()
# print(song.song_text)

# song = json.loads(song.song_text)
# print(song["Chour"])