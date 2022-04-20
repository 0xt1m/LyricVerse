def song_spliter1(song_text):
	def split_by_spaces(text):
		output = []
		word = ""
		for i in text:
			if i == " ":
				output.append(word)
				word = ""
			elif i == "\n":
				word += "\n"
				output.append(word)
				word = ""
			else:
				word += i
		output.append(word)
		return output

	song = {}
	song_split = split_by_spaces(song_text)
	chorus = ""
	for wordIndex in range(len(song_split)):
		if song_split[wordIndex].lower().strip() == "приспів" or song_split[wordIndex].lower().strip() == "приспів:":
			for w in range(wordIndex + 1, len(song_split)):
				if song_split[w].lower().strip() == "куплет" or song_split[w].lower().strip() == "куплет:":
					break
				chorus += song_split[w]
				if song_split[w][-1] != "\n":
					chorus += " "
			break
	song["chorus"] = chorus.strip()

	couplets = []
	couplet = ""
	for wordIndex in range(len(song_split)):
		if song_split[wordIndex].lower() == "куплет":
			for w in range(wordIndex + 1, len(song_split)):
				# print(song_split[w].lower())
				if song_split[w].lower().strip() == "приспів" or song_split[w].lower().strip() == "приспів:" or song_split[w].lower().strip() == "куплет":
					break
				couplet += song_split[w]
				if song_split[w][-1] != "\n":
					couplet += " "
			if int(couplet[0]):
				couplet = couplet[1:]
			couplets.append(couplet.strip())
			couplet = ""
			continue
	song["couplets"] = couplets
	return song



def song_spliter(song_text):
	return song_text.split("\n")