from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SmartLabel(QLabel):
	def __init__(self, screen):
		super().__init__(screen)

	def ownWordWrap(self, max_font_size=150):
		def calculate_text_size(text, font):
			self.setFont(font)
			metrics = self.fontMetrics()
			bounding_rect = metrics.boundingRect(0, 0, self.size().width(), 0, Qt.TextWordWrap, text)
			return bounding_rect.height()

		font_size = 10
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
				if current_width > self.size().width():  # Line exceeds widget width
					ready_text += active_text.strip() + "\n"
					active_text = ""
				active_text += word + " "
			ready_text += active_text.strip()

			# Check if text fits within the widget height
			current_height = calculate_text_size(ready_text, font)
			if current_height > self.size().height():  # Text exceeds widget height
				while current_height > self.size().height() and font_size > 10:
					font_size -= 2  # Decrease font size
					font.setPointSize(font_size)
					self.setFont(font)
					current_height = calculate_text_size(ready_text, font)
				break

			font_size += 2

		# Apply final text and font
		font.setPointSize(font_size)
		self.setFont(font)
		self.setText(ready_text.strip())
