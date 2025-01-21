from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

class CustomItem(QWidget):
	def __init__(self, text, item_type):
		super().__init__()

		self.item_type = item_type
		self.text = text

		self.setObjectName("CustomItem")
		self.textQVBoxLayout = QVBoxLayout()
		self.textQVBoxLayout.setSpacing(7)
		if item_type != "part":
			self.textUp = QLabel()
			self.textUp.setObjectName("textUp")
		self.textDown = QLabel()
		self.textDown.setObjectName("textDown")
		if item_type != "part":
			self.textQVBoxLayout.addWidget(self.textUp)
		self.textQVBoxLayout.addWidget(self.textDown)

		self.textDown.setText(self.text)

		self.allQHBoxLayout = QHBoxLayout()
		self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 0)

		if item_type != "part":
			if item_type == "couplet":
				self.textUp.setText("Куплет")

			elif item_type == "chorus":
				self.textUp.setText("Приспів")

			elif item_type == "bridge":
				self.textUp.setText("Брідж")



		self.setStyleSheet("""
			#textUp {
				color: #044c87;
			}
			#textDown {
				color: black;
			}
			""")

		self.setLayout(self.allQHBoxLayout)