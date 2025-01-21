from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from custom_item import CustomItem
from song import SongItem

import json
import sqlite3


class AddSongWindow:
    def __init__(self, songbook, ui):
        self.ui = ui
        self.songbook = songbook

        self.chorus = ""
        self.chorus_item = None
        self.couplets = []
        self.bridges = []

        # Connect signals to slots
        self.ui.add_couplet_btn.clicked.connect(self.add_couplet)
        self.ui.add_chorus_btn.clicked.connect(self.add_chorus)
        self.ui.add_bridge_btn.clicked.connect(self.add_bridge)
        self.ui.remove_item_btn.clicked.connect(self.remove_item)
        self.ui.save_item_btn.clicked.connect(self.save_song_item)
        self.ui.add_song_btn.clicked.connect(self.add_song)

    def addCustomItem(self, text, item_type):
        custom_item = CustomItem(text, item_type)
        simple_item = SongItem(text, item_type)
        if item_type != "bridge":
            simple_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        simple_item.setSizeHint(custom_item.sizeHint())

        self.ui.song_list.addItem(simple_item)
        self.ui.song_list.setItemWidget(simple_item, custom_item)

    def insertCustomItem(self, text, item_type, index):
        custom_item = CustomItem(text, item_type)
        simple_item = SongItem(text, item_type)
        if item_type != "bridge":
            simple_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        simple_item.setSizeHint(custom_item.sizeHint())

        self.ui.song_list.insertItem(index, simple_item)
        self.ui.song_list.setItemWidget(simple_item, custom_item)

    def add_couplet(self):
        couplet_text = self.ui.text_input.toPlainText().strip()
        if couplet_text:
            self.addCustomItem(couplet_text, "couplet")
            self.ui.text_input.clear()
            self.couplets.append(couplet_text)

            if self.chorus:
                self.addCustomItem(self.chorus, "chorus")

    def add_chorus(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")

        chorus_text = self.ui.text_input.toPlainText().strip()
        couplet_indeces = []
        for x in range(self.ui.song_list.count()):
            x_item = self.ui.song_list.item(x)
            if x_item.item_type == "couplet":
                couplet_indeces.append(x)
        if chorus_text and not self.chorus and couplet_indeces:
            for i in range(len(couplet_indeces) -1, -1, -1):
                self.insertCustomItem(chorus_text, "chorus", couplet_indeces[i] + 1)

            self.ui.text_input.clear()
            self.chorus = chorus_text
        elif self.chorus:
            msg.setText("Chorus already exists")
            msg.exec_()
        else:
            msg.setText("Add one couplet first")
            msg.exec_()

    def add_bridge(self):
        bridge_text = self.ui.text_input.toPlainText().strip()
        if bridge_text:
            self.addCustomItem(bridge_text, "bridge")
            self.ui.text_input.clear()
            self.bridges.append(bridge_text)

    def remove_item(self):
        current_item_index = self.ui.song_list.currentRow()
        if current_item_index != -1:
            item = self.ui.song_list.item(current_item_index)
            if item.item_type == "chorus":
                self.chorus = ""
                chorus_indeces = []
                for x in range(self.ui.song_list.count()):
                    x_item = self.ui.song_list.item(x)
                    if x_item.item_type == "chorus":
                        chorus_indeces.append(x)
                for i in range(len(chorus_indeces) - 1, -1, -1):
                    self.ui.song_list.takeItem(chorus_indeces[i])

            elif item.item_type == "couplet":
                self.ui.song_list.takeItem(current_item_index)
                if self.chorus:
                    self.ui.song_list.takeItem(current_item_index)
                if self.chorus and self.ui.song_list.count() == 0:
                    self.chorus = ""
            elif item.item_type == "bridge":
                self.ui.song_list.takeItem(current_item_index)

    def save_song_item(self):
        self.ui.save_item_btn.setEnabled(False)
        current_text = self.ui.text_input.toPlainText()
        current_item = self.ui.song_list.currentItem()
        current_item.text = current_text

        if current_item.item_type == "couplet":
            custom_item = CustomItem(current_text, "couplet")
            current_item.setSizeHint(custom_item.sizeHint())
            self.ui.song_list.setItemWidget(current_item, custom_item)
        elif current_item.item_type == "chorus":
            for x in range(self.ui.song_list.count()):
                x_item = self.ui.song_list.item(x)
                if x_item.item_type == "chorus":
                    custom_item = CustomItem(current_text, "chorus")
                    x_item.setSizeHint(custom_item.sizeHint())
                    self.ui.song_list.setItemWidget(x_item, custom_item)
                    x_item.text = current_text
        elif current_item.item_type == "bridge":
            custom_item = CustomItem(current_text, "bridge")
            current_item.setSizeHint(custom_item.sizeHint())
            self.ui.song_list.setItemWidget(current_item, custom_item)

        self.ui.text_input.clear()

    def add_song(self):
        with open("Songbooks/songbooks.json", "r") as jsonfile:
            songbooks = json.load(jsonfile)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")

        filename = songbooks[self.songbook]["filename"]

        song_title = self.ui.song_title.text()
        is_song_text = self.ui.song_list.count()
        if not song_title:
            msg.setText("Song must have a title!")
            msg.exec_()
        elif not is_song_text:
            msg.setText("Song must have text!")
            msg.exec_()
        else:
            couplets = []
            chorus = ""
            bridges = []
            for x in range(self.ui.song_list.count()):
                x_item = self.ui.song_list.item(x)
                if x_item.item_type == "couplet":
                    couplets.append(x_item.text)
                elif not chorus and x_item.item_type == "chorus":
                    chorus = x_item.text
                elif x_item.item_type == "bridge":
                    bridges.append({"text": x_item.text, "index": x})

            song_text = {
                "Couplets": couplets,
                "chorus": chorus,
                "Bridges": bridges
            }
            song_text = json.dumps(song_text, indent=4)

            connection = sqlite3.connect(f"Songbooks/{filename}")
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO Songs (title, song_text) VALUES ('{song_title}', '{song_text}')")
            connection.commit()

            self.ui.close()


class Ui_AddSongWindow:
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("New Song")
        MainWindow.setGeometry(100, 100, 738, 540)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.song_title = QtWidgets.QLineEdit(self.centralwidget)
        self.song_title.setGeometry(QtCore.QRect(10, 10, 310, 20))

        self.add_couplet_btn = QtWidgets.QPushButton("Add Couplet", self.centralwidget)
        self.add_couplet_btn.setGeometry(QtCore.QRect(10, 320, 111, 23))

        self.add_chorus_btn = QtWidgets.QPushButton("Add Chorus", self.centralwidget)
        self.add_chorus_btn.setGeometry(QtCore.QRect(120, 320, 111, 23))

        self.add_bridge_btn = QtWidgets.QPushButton("Add Bridge", self.centralwidget)
        self.add_bridge_btn.setGeometry(QtCore.QRect(120, 350, 111, 23))

        self.remove_item_btn = QtWidgets.QPushButton("Remove Item", self.centralwidget)
        self.remove_item_btn.setGeometry(QtCore.QRect(10, 350, 111, 23))

        self.save_item_btn = QtWidgets.QPushButton("Save", self.centralwidget)
        self.save_item_btn.setGeometry(QtCore.QRect(230, 320, 75, 23))
        self.save_item_btn.setEnabled(False)

        self.add_song_btn = QtWidgets.QPushButton("Add Song", self.centralwidget)
        self.add_song_btn.setGeometry(QtCore.QRect(80, 480, 141, 41))

        self.text_input = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.text_input.setGeometry(QtCore.QRect(10, 130, 301, 181))

        self.song_list = QtWidgets.QListWidget(self.centralwidget)
        self.song_list.setGeometry(QtCore.QRect(330, 10, 401, 521))
        self.song_list.setDragEnabled(False)
        self.song_list.setDragDropOverwriteMode(False)
        self.song_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Styling
        self.song_list.setStyleSheet("""
            ::item {
                background-color: white;
                border: 1px solid black;
                border-radius: 10px;
            }
            ::item:selected{
                border: 2px solid #c5cc04;
            }
        """)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AddSongWindow = QtWidgets.QMainWindow()
    ui = Ui_AddSongWindow()
    ui.setupUi(AddSongWindow)
    AddSongWindow.show()
    sys.exit(app.exec_())

