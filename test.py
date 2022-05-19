import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.textQVBoxLayout = QVBoxLayout()
        self.textUp = QLabel()
        self.textDown = QLabel()
        self.textQVBoxLayout.addWidget(self.textUp)
        self.textQVBoxLayout.addWidget(self.textDown)

        self.allQHBoxLayout = QHBoxLayout()
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 0)

        self.setLayout(self.allQHBoxLayout)

        self.textUp.setStyleSheet('''
            color: rgb(0, 0, 255);
        ''')
        self.textDown.setStyleSheet('''
            color: rgb(255, 0, 0);
        ''')

    def setTextUp(self, text):
        self.textUp.setText(text)

    def setTextDown(self, text):
        self.textDown.setText(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.list_widget = QListWidget(self)

        custom_widget = CustomWidget()
        custom_widget.setTextUp("Text up")
        custom_widget.setTextDown("Text down")

        simple_item = QListWidgetItem(self.list_widget)
        simple_item.setSizeHint(custom_widget.sizeHint())

        self.list_widget.addItem(simple_item)
        self.list_widget.setItemWidget(simple_item, custom_widget)

        self.setCentralWidget(self.list_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = MainWindow()
    application.show()

    sys.exit(app.exec())
