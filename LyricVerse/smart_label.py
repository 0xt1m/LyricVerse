from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont

class SmartLabel(QLabel):
	def __init__(self, screen):
		super().__init__(screen)

	def ownWordWrap(self, max_font_size=150):
		def calculate_text_size(text, font):
			self.setFont(font)
			metrics = self.fontMetrics()
			height = metrics.boundingRect(text).height()
			lines = len(text.split("\n"))
			return height * lines

		font_size = 2
		ready_text = ""
		while font_size <= max_font_size:
			# Set font size
			font = QFont("Arial", font_size)
			font.setBold(True)
			self.setFont(font)

			# Recalculate wrapped text
			words = self.text().split()
			ready_text = ""
			active_text = ""
			for word in words:
				current_width = self.fontMetrics().boundingRect(active_text + word + " ").width()
				if current_width > self.size().width():
					ready_text += active_text.strip() + "\n"
					active_text = ""
				active_text += word + " "
			ready_text += active_text.strip()

			# Check if text fits
			current_height = calculate_text_size(ready_text, font)
			if current_height > self.size().height():
				font_size -= 2  # Step back to the previous valid font size
				break

			font_size += 2

		# Apply final text and font
		font.setPointSize(font_size)
		self.setFont(font)
		self.setText(ready_text.strip())