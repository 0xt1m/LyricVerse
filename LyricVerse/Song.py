import json

from PyQt5.QtWidgets import QListWidgetItem


class Song:
    def __init__(self, number, title, song_text):
        self.number = number
        self.title = title
        self.song_text = song_text.strip()
        self.song_list = self._parse_song_parts()

    def _parse_song_parts(self):
        """Parse the song into parts based on section keywords."""
        song_text_lines = self.song_text.split("\n")
        song_parts = []
        current_part = []

        for line in song_text_lines:
            if any(keyword in line.lower() for keyword in ["куплет", "приспів", "припев"]):
                if current_part:
                    song_parts.append("\n".join(current_part))
                current_part = [line]
            else:
                current_part.append(line)

        if current_part:
            song_parts.append("\n".join(current_part))
        return song_parts

    def _get_parts(self, keywords):
        """Extract parts of the song based on specific keywords."""
        return [
            "\n".join(part.split("\n")[1:]).strip()
            for part in self.song_list
            if any(keyword in part.split("\n")[0].lower() for keyword in keywords)
        ]

    def _get_couplets(self):
        """Get all couplets."""
        return self._get_parts(["куплет"])

    def _get_chorus(self):
        """Get the first chorus."""
        choruses = self._get_parts(["приспів", "припев"])
        return choruses[0] if choruses else ""

    def reformat_text_to_json(self):
        """Convert the song into a structured JSON format."""
        song_data = {
            "Couplets": self._get_couplets(),
            "Chorus": self._get_chorus(),
            "Bridges": []
        }
        self.song_text = json.dumps(song_data, indent=4)

    def _wrap_text(self, text, max_length=50):
        """Wrap the text to the specified maximum line length."""
        words = text.split()
        lines, line = [], []

        for word in words:
            if len(" ".join(line + [word])) <= max_length:
                line.append(word)
            else:
                lines.append(" ".join(line))
                line = [word]

        if line:
            lines.append(" ".join(line))
        return "\n".join(lines)

    def set_text_wrap(self, max_length=50):
        """Wrap the song text to a specific line length."""
        self.song_text = self._wrap_text(self.song_text, max_length)
        

class SongLine:
	def __init__(self, text, wholePart, index_from):
		self.text = text
		self.index_from = index_from
		self.wholePart = wholePart
	

class SongItem(QListWidgetItem):
	def __init__(self, text, item_type):
		super().__init__()

		self.item_type = item_type
		self.text = text
