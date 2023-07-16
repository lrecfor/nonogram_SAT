from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
import enum
from PyQt6 import QtCore


severalButtons = 0
buttonMoveStatus = -1


class Status(enum.Enum):
    white = 0
    cross = 1
    black = 2


class PushButton(QPushButton):
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.num = number
        self.status = Status.white
        self.size = 20
        self.setFixedSize(self.size, self.size)
        self.setStyleSheet("QPushButton { background-color: white }")

    def mousePressEvent(self, event: QMouseEvent):
        global buttonMoveStatus
        if event.button() != QtCore.Qt.MouseButton.LeftButton and event.button() != QtCore.Qt.MouseButton.RightButton and \
                event.buttons() != QtCore.Qt.MouseButton.LeftButton and event.buttons() != QtCore.Qt.MouseButton.RightButton:
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            global buttonMoveStatus
            buttonMoveStatus = self.status
            if self.status == Status.black:
                self.status = Status.white
                self.setStyleSheet("QPushButton { background-color: white }")
                return
            elif self.status == Status.cross:
                self.status = Status.white
                self.setText("")

            self.setStyleSheet("QPushButton { background-color: black }")
            self.status = Status.black

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            buttonMoveStatus = self.status
            if self.status == Status.cross:
                self.status = Status.white
                self.setText("")
                return
            elif self.status == Status.black:
                self.status = Status.white
                self.setStyleSheet("QPushButton { background-color: white }")
                return

            self.setText("X")
            self.status = Status.cross

        elif event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            if buttonMoveStatus == Status.black:
                self.status = Status.white
                self.setStyleSheet("QPushButton { background-color: white }")
                self.setText("")
                return
            elif buttonMoveStatus == Status.white:
                if self.status == Status.cross:
                    self.setText("")

            self.setStyleSheet("QPushButton { background-color: black }")
            self.status = Status.black

        elif event.buttons() == QtCore.Qt.MouseButton.RightButton:
            if buttonMoveStatus == Status.cross:
                self.status = Status.white
                self.setText("")
                self.setStyleSheet("QPushButton { background-color: white }")
                return

            self.setStyleSheet("QPushButton { background-color: white }")
            self.setText("X")
            self.status = Status.cross


