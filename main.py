from nonogram import Nonogram
import time
import sys
import random
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from mainwindow import MainWindow

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # n = Nonogram()
    # n.logic_solve()
    # # n.print_nonogram(n.solution)
    #
    # # без первичной обработки, только SAT
    # a = time.time()
    # without_ = n.solve()
    # print("WITHOUT: ", time.time() - a)
    #
    # print("\n\n")
    #
    # # с первичной обработкой и SAT
    # a = time.time()
    # with_ = n.solve(with_=True)
    # print("WITH: ", time.time() - a)
    #
    # print("\n\nRESULT: ", without_ == with_)

    if __name__ == "__main__":
        random.seed()
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        # Установка заголовка окна
        main_window.setWindowTitle("Nonogram")
        # main_window.showMaximized()
        sys.exit(app.exec())
