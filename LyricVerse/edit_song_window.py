from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsRectItem, QMessageBox, QMainWindow
import json
import sqlite3

class EditSongWindow(QMainWindow):
    def __init__(self, songbook, song):
        super().__init__()
        self.ui = Ui_EditSongWindow()
        self.ui.setupUi(self)
        self.songbook = songbook
        self.song = song
        self.init_ui()

    def init_ui(self):
        self.ui.song_list.setSpacing(2)
        self.ui.add_couplet_btn.clicked.connect(self.add_couplet)
        self.ui.add_chorus_btn.clicked.connect(self.add_chorus)
        self.ui.add_bridge_btn.clicked.connect(self.add_bridge)
        self.ui.remove_item_btn.clicked.connect(self.remove_item)
        self.ui.song_list.itemDoubleClicked.connect(self.edit_song_item)
        self.ui.save_item_btn.clicked.connect(self.save_song_item)
        self.ui.edit_song_btn.clicked.connect(self.edit_song)

        self.ui.save_item_btn.setEnabled(False)
        self.chorus = ""

        self.ui.song_title.setText(self.song.title)

        song_text = json.loads(self.song.song_text)
        song_couplets = song_text["Couplets"]
        self.chorus = song_text["Chorus"]
        song_bridges = song_text["Bridges"]

        self.scene = QGraphicsScene(self)
        self.canvas = QGraphicsView(self.scene, self)
        self.canvas.setGeometry(330, 10, 401, 521)
        self.canvas.setRenderHint(QtGui.QPainter.Antialiasing)
        self.canvas.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        self.add_song_items(song_couplets, song_bridges)

    def add_song_items(self, song_couplets, song_bridges):
        y_offset = 0
        for couplet in song_couplets:
            self.add_item_to_canvas(couplet, y_offset)
            y_offset += 40  # Space between items
        if self.chorus:
            self.add_item_to_canvas(self.chorus, y_offset)
            y_offset += 40
        for bridge in song_bridges:
            self.add_item_to_canvas(bridge["text"], y_offset)
            y_offset += 40

    def add_item_to_canvas(self, text, y_offset):
        text_item = QGraphicsTextItem(text)
        text_item.setFont(QtGui.QFont('Arial', 14))
        text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        text_item.setPos(10, y_offset)
        rect = QGraphicsRectItem(text_item.boundingRect())
        rect.setPen(QtGui.QPen(QtCore.Qt.black))
        rect.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.scene.addItem(rect)
        self.scene.addItem(text_item)

    def edit_song_item(self):
        current_item = self.ui.song_list.currentItem()
        self.ui.text_input.clear()
        self.ui.text_input.appendPlainText(current_item.text)

    def save_song_item(self):
        self.ui.save_item_btn.setEnabled(False)
        current_text = self.ui.text_input.toPlainText()
        current_item = self.ui.song_list.currentItem()
        current_item.text = current_text

        for item in self.scene.items():
            if isinstance(item, QGraphicsTextItem) and item.toPlainText() == current_item.text:
                item.setPlainText(current_text)

        self.ui.text_input.clear()

    def add_couplet(self):
        couplet_text = self.ui.text_input.toPlainText().strip()
        if couplet_text:
            self.add_item_to_canvas(couplet_text, len(self.scene.items()) * 40)
            self.ui.text_input.clear()
            if self.chorus:
                self.add_item_to_canvas(self.chorus, len(self.scene.items()) * 40)

    def add_chorus(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")

        chorus_text = self.ui.text_input.toPlainText().strip()
        if chorus_text and not self.chorus:
            self.add_item_to_canvas(chorus_text, len(self.scene.items()) * 40)
            self.ui.text_input.clear()
            self.chorus = chorus_text
        elif self.chorus:
            msg.setText("Chorus already exists")
            msg.exec_()

    def add_bridge(self):
        bridge_text = self.ui.text_input.toPlainText().strip()
        if bridge_text:
            self.add_item_to_canvas(bridge_text, len(self.scene.items()) * 40)
            self.ui.text_input.clear()

    def remove_item(self):
        current_item_index = self.ui.song_list.currentRow()
        if current_item_index != -1:
            item = self.ui.song_list.item(current_item_index)
            if item.item_type == "chorus":
                self.chorus = ""
            self.ui.song_list.takeItem(current_item_index)

    def edit_song(self):
        with open("Songbooks/songbooks.json", "r") as jsonfile:
            songbooks = json.load(jsonfile)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")

        filename = songbooks[self.songbook]["filename"]

        song_title = self.ui.song_title.text().strip()
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
            for item in self.scene.items():
                if isinstance(item, QGraphicsTextItem):
                    if "Couplet" in item.toPlainText():
                        couplets.append(item.toPlainText())
                    elif "Chorus" in item.toPlainText():
                        chorus = item.toPlainText()
                    elif "Bridge" in item.toPlainText():
                        bridges.append({"text": item.toPlainText(), "index": item.y()})

            song_text = {
                "Couplets": couplets,
                "Chorus": chorus,
                "Bridges": bridges
            }
            song_text = json.dumps(song_text, indent=4)

            connection = sqlite3.connect(f"Songbooks/{filename}")
            cursor = connection.cursor()
            cursor.execute(f"UPDATE Songs SET title=?, song_text=? WHERE id={self.song.number}", (song_title, song_text))
            connection.commit()

            self.close()

class Ui_EditSongWindow(object):
    def setupUi(self, EditSongWindow):
        EditSongWindow.setObjectName("EditSongWindow")
        EditSongWindow.resize(740, 542)
        self.centralwidget = QtWidgets.QWidget(EditSongWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.save_item_btn = QtWidgets.QPushButton(self.centralwidget)
        self.save_item_btn.setGeometry(QtCore.QRect(230, 320, 75, 23))
        self.save_item_btn.setObjectName("save_item_btn")
        self.edit_song_btn = QtWidgets.QPushButton(self.centralwidget)
        self.edit_song_btn.setGeometry(QtCore.QRect(80, 480, 141, 41))
        self.edit_song_btn.setObjectName("edit_song_btn")
        self.add_bridge_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_bridge_btn.setGeometry(QtCore.QRect(120, 350, 111, 23))
        self.add_bridge_btn.setObjectName("add_bridge_btn")
        self.song_title = QtWidgets.QLineEdit(self.centralwidget)
        self.song_title.setGeometry(QtCore.QRect(10, 10, 310, 20))
        self.song_title.setObjectName("song_title")
        self.add_couplet_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_couplet_btn.setGeometry(QtCore.QRect(10, 320, 111, 23))
        self.add_couplet_btn.setObjectName("add_couplet_btn")
        self.remove_item_btn = QtWidgets.QPushButton(self.centralwidget)
        self.remove_item_btn.setGeometry(QtCore.QRect(10, 350, 111, 23))
        self.remove_item_btn.setObjectName("remove_item_btn")
        self.add_chorus_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_chorus_btn.setGeometry(QtCore.QRect(120, 320, 111, 23))
        self.add_chorus_btn.setObjectName("add_chorus_btn")
        self.song_list = QtWidgets.QListWidget(self.centralwidget)
        self.song_list.setGeometry(QtCore.QRect(330, 10, 401, 521))
        self.song_list.setDragEnabled(False)
        self.song_list.setDragDropOverwriteMode(False)
        self.song_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.song_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.song_list.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.song_list.setUniformItemSizes(False)
        self.song_list.setObjectName("song_list")
        self.text_input = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.text_input.setGeometry(QtCore.QRect(10, 130, 311, 181))
        self.text_input.setObjectName("text_input")
        EditSongWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(EditSongWindow)
        QtCore.QMetaObject.connectSlotsByName(EditSongWindow)

    def retranslateUi(self, EditSongWindow):
        _translate = QtCore.QCoreApplication.translate
        EditSongWindow.setWindowTitle(_translate("EditSongWindow", "Edit song"))
        self.save_item_btn.setText(_translate("EditSongWindow", "Save"))
        self.edit_song_btn.setText(_translate("EditSongWindow", "Edit song"))
        self.add_bridge_btn.setText(_translate("EditSongWindow", "Add bridge"))
        self.song_title.setPlaceholderText(_translate("EditSongWindow", "Enter song title"))
        self.add_couplet_btn.setText(_translate("EditSongWindow", "Add couplet"))
        self.remove_item_btn.setText(_translate("EditSongWindow", "Remove item"))
        self.add_chorus_btn.setText(_translate("EditSongWindow", "Add chorus"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EditSongWindow = QtWidgets.QMainWindow()
    ui = Ui_EditSongWindow()
    ui.setupUi(EditSongWindow)
    EditSongWindow.show()
    sys.exit(app.exec_())
