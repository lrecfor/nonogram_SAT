import sys
import random
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, QEvent, QPoint, QPointF, QCoreApplication
from PyQt6.QtGui import QMouseEvent, QPointingDevice
import os
from pushbutton import PushButton, Status
from nonogram import Nonogram


uploadFlag = 0
path_ = "./"
nonogramName = ""


class MainWindow(QMainWindow):
    @staticmethod
    def exit():
        sys.exit()

    def check_nonogram(self):
        # Функция проверки решения
        if self.grid.count() == 0:
            return

        buttonStatus = []
        for button in self.puzzle:
            if button.status == Status.black:
                buttonStatus.append(1)
            elif button.status == Status.white:
                buttonStatus.append(0)

        solution = self.get_solution()  # получаем правильное решение кроссворда

        if buttonStatus == solution:
            text = "Solution is OK."
        else:
            text = "There are errors in your solution."

        print("check_nonogram():", text)
        msgBox = QMessageBox()
        horizontalSpacer = QSpacerItem(200, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        msgBox.setText(text)
        msgBox.setWindowTitle("Checking solution")
        layout = msgBox.layout()
        layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
        msgBox.exec()

    def get_solution(self):
        n = Nonogram(self.width, self.height, self.nonogram_cols, self.nonogram_rows)
        result_ = n.solve()
        result = []
        for i in result_:
            if i < 0:
                result.append(0)
            else:
                result.append(1)
        return result

    def clear_nonogram(self):
        # Функция очистки решения
        if self.grid.count():
            for button in self.puzzle:
                button.status = Status.white
                button.setText("")
                button.setStyleSheet("QPushButton { background-color: white }")

    def upload_nonogram(self):
        # Функция загрузки решения из файла
        global uploadFlag
        global nonogramName
        uploadFlag = 1
        usersFilename, _ = QFileDialog.getOpenFileName(self, "Select source file", path_, "Text files (*.txt)")
        if usersFilename == "":
            return
        nonogramName = usersFilename
        print("upload_nonogram():", nonogramName)
        self.clear_field()
        self.build_nonogram()

    def random_nonogram(self):
        # Функция генерации случайного решения
        global nonogramName
        self.clear_field()
        self.get_nonograms_fr_dir()
        nonogram = random.choice(self.nonograms)
        nonogramName = nonogram
        print("random_nonogram():", nonogram)
        self.build_nonogram()

    def mouseMoveEvent(self, event):
        # Обработчик события движения мыши
        for button in self.puzzle:
            buttonRect = button.rect().translated(button.mapToGlobal(QPoint(0, 0)))
            if buttonRect.contains(QMouseEvent.globalPosition(event).toPoint()):
                clickEvent = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(button.pos()), QPointF(button.pos()), event.button(),
                                         event.buttons(),
                                         QMouseEvent.modifiers(event).NoModifier, QPointingDevice.primaryPointingDevice())
                clickEvent.setAccepted(True)
                QCoreApplication.sendEvent(button, clickEvent)
                break

    def get_nonograms_fr_dir(self):
        path = path_
        for entry in os.scandir(path):
            if entry.is_file() and entry.name.endswith('.txt'):
                self.nonograms.append(entry.path)

    def nonogram_fr_file(self, filename):
        with open(filename, 'r') as file:
            self.nonogram_rows = []
            self.nonogram_cols = []
            for line in file:
                line = line.strip()
                if line:
                    row = [int(substring) for substring in line.split()]
                    self.nonogram_rows.append(row)
                else:
                    break

            for line in file:
                line = line.strip()
                if line:
                    col = [int(substring) for substring in line.split()]
                    self.nonogram_cols.append(col)
                else:
                    break

        self.width = len(self.nonogram_cols)
        self.height = len(self.nonogram_rows)

    def fill_cols_labels(self):
        spacer_x = 0
        for i in range(self.width):
            str_ = ""
            for j in range(len(self.nonogram_cols[i])):
                num = str(self.nonogram_cols[i][j])
                if num == '0':
                    break
                str_ += num
                if j < len(self.nonogram_cols[i]) - 1:
                    str_ += "\n"

            label = QLabel(str_)
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignCenter)
            self.cols.append(label)

            if i > 0 and i % 5 == 0:
                spacer_x += 1
                self.grid.setColumnMinimumWidth(i + spacer_x, 2)

            self.grid.addWidget(label, 0, i + spacer_x + 1)

    def fill_rows_labels(self):
        spacer_y = 0
        for i in range(self.height):
            str_ = " "
            for j in range(len(self.nonogram_rows[i])):
                num = str(self.nonogram_rows[i][j])
                if num == '0':
                    break
                str_ += num
                if j == len(self.nonogram_rows[i]) - 1:
                    str_ += " "
                else:
                    str_ += "  "

            label = QLabel(str_)
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            self.rows.append(label)

            if i > 0 and i % 5 == 0:
                spacer_y += 1
                self.grid.setRowMinimumHeight(i + spacer_y, 2)

            self.grid.addWidget(label, i + spacer_y + 1, 0)

    def build_nonogram(self):
        global uploadFlag
        if uploadFlag == 1:
            uploadFlag = 0

        self.nonogram_fr_file(nonogramName)

        self.fill_cols_labels()
        self.fill_rows_labels()

        spacer_y = 0
        spacer_x = 0
        pos = 0
        for i in range(self.height):
            if i > 0 and i % 5 == 0:
                spacer_y += 1
            spacer_x = 0
            for j in range(self.width):
                if j > 0 and j % 5 == 0:
                    spacer_x += 1
                pos = i * self.width + j
                button = PushButton(pos)
                self.puzzle.append(button)
                self.grid.addWidget(button, i + spacer_y + 1, j + spacer_x + 1)

        self.buttonStatus = [None] * len(self.puzzle)

    def clear_field(self):
        while self.grid.count():
            widget = self.grid.itemAt(0).widget()
            if widget:
                self.grid.removeWidget(widget)
                widget.deleteLater()

        self.puzzle.clear()
        self.nonograms.clear()
        self.nonogram_cols.clear()
        self.nonogram_rows.clear()
        self.cols.clear()
        self.rows.clear()

    def __init__(self):
        QMainWindow.__init__(self, parent=None)

        super().__init__()
        self.cols = []
        self.rows = []
        self.nonograms = []
        self.nonogram_rows = []
        self.nonogram_cols = []

        self.width = 0
        self.height = 0

        self.buttonStatus = []
        self.puzzle = []

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setWidget(QWidget())

        self.window = QWidget()
        self.layout = QVBoxLayout(self.window)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignCenter)

        self.top = QHBoxLayout()
        self.top.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignCenter)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignCenter)

        self.scroll.widget().setLayout(self.grid)

        self.exitButton = QPushButton("Exit", self)
        self.checkButton = QPushButton("Check", self)
        self.clearButton = QPushButton("Clear", self)
        self.uploadButton = QPushButton("Upload", self)
        self.randomButton = QPushButton("Random", self)

        self.exitButton.clicked.connect(self.exit)
        self.checkButton.clicked.connect(self.check_nonogram)
        self.clearButton.clicked.connect(self.clear_nonogram)
        self.uploadButton.clicked.connect(self.upload_nonogram)
        self.randomButton.clicked.connect(self.random_nonogram)

        self.setCentralWidget(self.window)

        self.top.addWidget(self.randomButton)
        self.top.addWidget(self.clearButton)
        self.top.addWidget(self.uploadButton)
        self.top.addWidget(self.checkButton)
        self.top.addWidget(self.exitButton)

        self.layout.addLayout(self.top)
        self.layout.addLayout(self.grid)
        self.layout.addWidget(self.scroll)

        self.setMouseTracking(True)
