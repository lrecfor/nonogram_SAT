from pysat.solvers import *
import enum
import copy
import time


filename1 = "C:\\Users\\dana\\uni\\coursework\\japan.txt"
filename2 = "C:\\Users\\dana\\uni\\coursework\\japan_sol.txt"


class Status(enum.Enum):
    white = 0
    cross = 1
    black = 2


class Nonogram:
    # def __init__(self, w, h, nonogram_cols, nonogram_rows):
    #     self.width = w
    #     self.height = h
    #     self.cols = nonogram_cols
    #     self.rows = nonogram_rows
    #     self.solution = []
    #     self.filledCols = []
    #     self.filledRows = []
    #     self.colsValuesStatus = []
    #     self.rowsValuesStatus = []
    def __init__(self, filename="C:\\Users\\dana\\uni\\coursework\\japan.txt"):
        self.width = 0
        self.height = 0
        self.cols = []
        self.rows = []
        self.solution = []
        self.filledCols = []
        self.filledRows = []
        self.colsValuesStatus = []
        self.rowsValuesStatus = []

        file = open(filename1, "r")
        if file:
            lines = file.readlines()
            tmp = []
            for line in lines:
                if line == "\n":
                    break
                line = line.strip()
                numbers = line.split()
                tmp = [int(num) for num in numbers]
                self.rows.append(tmp)
                self.filledRows.append(False)
                tmp = []

            tmp = []
            for line in lines[len(self.rows) + 1:]:
                line = line.strip()
                numbers = line.split()
                tmp = [int(num) for num in numbers]
                self.cols.append(tmp)
                self.filledCols.append(False)
                tmp = []

        file.close()

        self.width = len(self.cols)
        self.height = len(self.rows)
        self.solution = [[Status.white] * self.width for _ in range(self.height)]
        self.colsValuesStatus = [[False] * len(col) for col in self.cols]
        self.rowsValuesStatus = [[False] * len(row) for row in self.rows]

    def printNonogram(self, nonogram):
        print("\t", end="")
        for j in range(self.width):
            if j > 9:
                print(j, "  ", end="")
            else:
                print(j, "   ", end="")
        print("\n")
        for j in range(self.height):
            print(j, "\t", end="")
            for k in range(self.width):
                if nonogram[j][k] == Status.black:
                    print("*", "   ", end="")
                elif nonogram[j][k] == Status.cross:
                    print("X", "   ", end="")
                elif nonogram[j][k] == Status.white:
                    print("-", "   ", end="")
            print("\n")

        print("\n\n")

    def sumCol(self, nonogram, col, kind):
        summa = 0
        for j in range(self.height):
            if nonogram[j][col] == kind:
                summa += 1

        return summa

    def sumRow(self, nonogram, row, kind):
        summa = 0
        for j in range(self.width):
            if nonogram[row][j] == kind:
                summa += 1

        return summa

    def calcColBias(self, nonogram, col):
        biasUp = 0  # смещение, если сверху есть отмеченные клетки
        biasDown = 0  # смещение, если снизу есть отмеченные клетки

        if nonogram[0][col] == Status.cross:
            for j in range(self.height):
                if nonogram[j][col] == Status.white and biasUp > 0:
                    break
                elif nonogram[j][col] == Status.cross:
                    biasUp += 1

        if nonogram[self.height - 1][col] == Status.cross:
            for j in range(self.height - 1, -1, -1):
                if nonogram[j][col] == Status.white and biasDown > 0:
                    break
                elif nonogram[j][col] == Status.cross:
                    biasDown += 1

        if biasUp == self.height:
            biasUp = 0

        if biasDown == self.height:
            biasDown = 0

        return biasUp, biasDown

    def calcRowBias(self, nonogram, row):
        biasLeft = 0  # смещение, если слева есть отмеченные клетки
        biasRight = 0  # смещение, если справа есть отмеченные клетки

        if self.solution[row][0] == Status.cross:
            for j in range(self.width):
                if self.solution[row][j] == Status.white and biasLeft > 0:
                    break
                elif self.solution[row][j] == Status.cross:
                    biasLeft += 1

        if self.solution[row][self.width - 1] == Status.cross:
            for j in range(self.width - 1, -1, -1):
                if self.solution[row][j] == Status.white and biasRight > 0:
                    break
                elif self.solution[row][j] == Status.cross:
                    biasRight += 1

        if biasLeft == self.width:
            biasLeft = 0

        if biasRight == self.width:
            biasRight = 0

        return biasLeft, biasRight

    def _convert(self, n, c, d=0, prec=list()):
        l = list(range(d, n - sum(c) - len(c) + 2))
        if len(c) == 1:
            for i in l:
                yield prec + [i]
        else:
            for i in l:
                yield from self._convert(n - i - c[0], c[1:], 1, prec + [i])

    def convert(self, n, c):
        c = [i for i in c if i != 0]
        if len(c) == 0:
            yield [-1] * n
            return
        for x in self._convert(n, c):
            l = [-1] * n
            pos = 0
            for y, z in zip(c, x):
                l[pos + z:pos + z + y] = [1] * y
                pos = pos + z + y
            yield l

    def calcSolution(self):
        affectedLines = []

        # первичная обработка пазла

        # пункт 1: пустые линии, полностью заполняемые
        for i in range(max(self.height, self.width)):
            if i < len(self.cols):
                # пункт 1.1: пустые столбцы
                if self.cols[i] == [0]:
                    for k in range(self.height):
                        self.solution[k][i] = Status.cross
                    self.filledCols[i] = True
                    self.colsValuesStatus[i] = [True] * len(self.colsValuesStatus[i])
                # пункт 1.2: полные столбцы
                elif self.cols[i] == [self.height]:
                    for k in range(self.height):
                        self.solution[k][i] = Status.black
                    self.filledCols[i] = True
                    self.colsValuesStatus[i] = [True] * len(self.colsValuesStatus[i])

            if i < len(self.rows):
                # пункт 1.1: пустые строки
                if self.rows[i] == [0]:
                    for k in range(self.width):
                        self.solution[i][k] = Status.cross
                    self.filledRows[i] = True
                    self.rowsValuesStatus[i] = [True] * len(self.rowsValuesStatus[i])
                # пункт 1.2: полные строки
                elif self.rows[i] == [self.width]:
                    for k in range(self.width):
                        self.solution[i][k] = Status.black
                    self.filledRows[i] = True
                    self.rowsValuesStatus[i] = [True] * len(self.rowsValuesStatus[i])

        # первичная обработка пазла
        while True:
            affectedLines.clear()
            for i in range(max(self.height, self.width)):
                copySolution = copy.deepcopy(self.solution)
                # столбцы
                if i < len(self.cols) and not self.filledCols[i]:
                    biasPair = self.calcColBias(self.solution, i)
                    biasUp = biasPair[0]  # смещение если сверху есть отмеченные клетки
                    biasDown = biasPair[1]  # смещение если снизу есть отмеченные клетки

                    # пункт 1.4: частично заполняемые линии
                    blockNumber = 0
                    blocksLen = sum(self.cols[i]) + (len(self.cols[i]) - 1) if len(self.cols[i]) > 1 else self.cols[i][0]
                    it = next((idx for idx, val in enumerate(self.cols[i]) if val > self.height - blocksLen), None)
                    if it is not None or self.cols[i][0] * 2 > self.height:
                        tmpUp = [Status.white] * (blocksLen + (self.height - blocksLen))
                        tmpDown = [Status.white] * (blocksLen + (self.height - blocksLen))
                        offset = biasUp
                        for j in range(len(self.cols[i])):
                            k = 0
                            while k < self.cols[i][j]:
                                if self.cols[i][j] > self.height - blocksLen:
                                    tmpUp[k + offset] = Status.black
                                k += 1
                            offset = offset + k + 1
                        for k in range(self.height):
                            if self.solution[k][i] == Status.cross:
                                tmpUp[k] = Status.white

                        offset = self.height - biasDown
                        for j in range(len(self.cols[i]) - 1, -1, -1):
                            k = self.cols[i][j]
                            while k > 0:
                                if self.cols[i][j] > self.height - blocksLen:
                                    tmpDown[offset - k] = Status.black
                                k -= 1
                            offset = offset - self.cols[i][j] - 1
                        for k in range(self.height):
                            if self.solution[k][i] == Status.cross:
                                tmpDown[k] = Status.white

                        pos = -1
                        length = 0
                        j = 0
                        while j < self.height:
                            if tmpUp[j] == Status.black and tmpDown[j] == Status.black:
                                pos = j
                                while j < self.height and (tmpUp[j] != Status.white and tmpDown[j] != Status.white):
                                    length += 1
                                    j += 1
                                for k in range(pos, pos + length):
                                    self.solution[k][i] = Status.black
                                pos = -1
                                length = 0
                                if blockNumber < len(self.cols[i]):
                                    j = (self.height - blocksLen - biasDown) + biasUp
                                    for v in range(blockNumber):
                                        j += self.cols[i][v]
                                    j += blockNumber - 1
                                    blockNumber += 1
                            j += 1

                    # пункт 3.1: проверка линий за закрашенность и отметка пропусков
                    if self.sumCol(self.solution, i, Status.black) != 0:
                        offset = 0  # смещение если сверху есть отмеченные клетки
                        stopFlag = False
                        for val in self.cols[i]:
                            stopFlag = True
                            while offset < self.height and self.solution[offset][i] != Status.black:
                                offset += 1
                            count = 0
                            while offset < self.height and self.solution[offset][i] == Status.black:
                                count += 1
                                offset += 1

                            if count != val:
                                break
                            stopFlag = False
                        if not stopFlag:
                            for j in range(self.height):
                                if self.solution[j][i] != Status.black:
                                    self.solution[j][i] = Status.cross
                            self.filledCols[i] = True

                    # пункт 3.2: полные столбцы с учетом пропусков по границам
                    if sum(self.cols[i]) + (len(self.cols[i]) - 1) + biasUp + biasDown == self.height:
                        offset = biasUp
                        for k in range(len(self.cols[i])):
                            pos = 0
                            while True:
                                pos += 1
                                if pos > self.cols[i][k]:
                                    break
                                self.solution[offset][i] = Status.black
                                offset += 1
                            if k != len(self.cols[i]) - 1:
                                self.solution[offset][i] = Status.cross
                                offset += 1
                        self.filledCols[i] = True

                    # пункт 4: столбцы с неотмеченными границами закрашенных блоков и незакрашенных блоков по периметру
                    if self.solution[0][i] == Status.black:
                        j = 0
                        while j < self.cols[i][0]:
                            if self.solution[j][i] == Status.cross:
                                break
                            if self.solution[j][i] != Status.black:
                                self.solution[j][i] = Status.black
                            j += 1
                        if self.solution[j][i] == Status.white:
                            self.solution[j][i] = Status.cross
                        self.colsValuesStatus[i][0] = True
                    if self.solution[self.height - 1][i] == Status.black:
                        j = self.height - 1
                        len_ = self.cols[i][len(self.cols[i]) - 1]
                        while j >= 0:
                            if len_ == 0 or self.solution[j][i] == Status.cross:
                                break
                            if self.solution[j][i] != Status.black:
                                self.solution[j][i] = Status.black
                            len_ -= 1
                            j -= 1
                        if self.solution[self.height - self.cols[i][len(self.cols[i]) - 1] - 1][i] == Status.white:
                            self.solution[self.height - self.cols[i][len(self.cols[i]) - 1] - 1][i] = Status.cross
                        self.colsValuesStatus[i][len(self.colsValuesStatus[i]) - 1] = True
                    if self.filledCols[i]:
                        self.colsValuesStatus[i] = [True] * len(self.colsValuesStatus[i])

                    # пункт 3.2.1: полные столбцы, имеющие закрашенные клетки по границам
                    if len(self.cols[i]) < 3 and (self.solution[0][i] == Status.black or self.solution[self.height - 1][i] == Status.black):
                        if len(self.cols[i]) == 2 and (
                                self.solution[0][i] != Status.black or self.solution[self.height - 1][i] != Status.black):
                            continue
                        if self.solution[0][i] == Status.black:
                            j = 0
                            while j < self.cols[i][0]:
                                if self.solution[j][i] == Status.cross:
                                    break
                                if self.solution[j][i] != Status.black:
                                    self.solution[j][i] = Status.black
                                j += 1

                        if self.solution[self.height - 1][i] == Status.black:
                            j = self.height - 1
                            length = self.cols[i][len(self.cols[i]) - 1]
                            while j >= 0:
                                if length == 0 or self.solution[j][i] == Status.cross:
                                    break
                                if self.solution[j][i] != Status.black:
                                    self.solution[j][i] = Status.black
                                length -= 1
                                j -= 1

                        for j in range(self.cols[i][0], self.height - self.cols[i][len(self.cols[i]) - 1]):
                            self.solution[j][i] = Status.cross
                        self.filledCols[i] = True

                if i < len(self.rows) and not self.filledRows[i]:
                    biasPair = self.calcRowBias(self.solution, i)
                    biasLeft = biasPair[0]  # смещение если сверху есть отмеченные клетки
                    biasRight = biasPair[1]  # смещение если снизу есть отмеченные клетки

                    # пункт 1.4: частично заполняемые линии
                    # если ширина пазла минус сумма занимаемых клеток в этой колонке равна какому - то числу != 0,
                    # то блок больше этой величины мб частично окрашен с помощью нахлёста
                    blockNumber = 0
                    blocksLen = sum(self.rows[i]) + (len(self.rows[i]) - 1) if len(self.rows[i]) > 1 else self.rows[i][
                        0]
                    it = next((idx for idx, val in enumerate(self.rows[i]) if val > self.width - blocksLen), None)
                    if it is not None or self.rows[i][0] * 2 > self.width:
                        tmpLeft = [Status.white] * (blocksLen + (self.width - blocksLen))
                        tmpRight = [Status.white] * (blocksLen + (self.width - blocksLen))
                        offset = biasLeft
                        for j in range(len(self.rows[i])):
                            k = 0
                            while k < self.rows[i][j]:
                                if self.rows[i][j] > self.width - blocksLen:
                                    tmpLeft[k + offset] = Status.black
                                if self.solution[i][k] == Status.cross:
                                    tmpLeft[k + offset] = Status.white
                                k += 1
                            offset = offset + k + 1
                        for k in range(self.width):
                            if self.solution[i][k] == Status.cross:
                                tmpLeft[k] = Status.white

                        offset = self.width - biasRight
                        j = len(self.rows[i]) - 1
                        while j >= 0:
                            k = self.rows[i][j]
                            while k > 0:
                                if self.rows[i][j] > self.width - blocksLen:
                                    tmpRight[offset - k] = Status.black
                                if self.solution[i][k] == Status.cross:
                                    tmpRight[offset - k] = Status.white
                                k -= 1
                            offset = offset - self.rows[i][j] - 1
                            j -= 1

                        for k in range(self.width):
                            if self.solution[i][k] == Status.cross:
                                tmpRight[k] = Status.white

                        pos = -1
                        length = 0
                        j = 0
                        while j < self.width:
                            if tmpLeft[j] == Status.black and tmpRight[j] == Status.black:
                                pos = j
                                while j < self.width and (tmpLeft[j] != Status.white and tmpRight[j] != Status.white):
                                    length += 1
                                    j += 1
                                for k in range(pos, pos + length):
                                    self.solution[i][k] = Status.black
                                pos = -1
                                length = 0
                                if blockNumber < len(self.rows[i]):
                                    j = (self.width - blocksLen - biasRight) + biasLeft
                                    for v in range(blockNumber):
                                        j += self.rows[i][v]
                                    j += blockNumber - 1
                                    blockNumber += 1
                            j += 1

                    # пункт 3.1: проверка линий за закрашеность и отметка пропусков
                    if self.sumRow(self.solution, i, Status.black) != 0:
                        offset = 0  # смещение если сверху есть отмеченные клетки
                        stopFlag = False
                        for val in self.rows[i]:
                            stopFlag = True
                            while offset < self.width and self.solution[i][offset] != Status.black:
                                offset += 1
                            count = 0
                            while offset < self.width and self.solution[i][offset] == Status.black:
                                count += 1
                                offset += 1

                            if count != val:
                                break
                            stopFlag = False
                        if not stopFlag:
                            for j in range(self.width):
                                if self.solution[i][j] != Status.black:
                                    self.solution[i][j] = Status.cross
                            self.filledRows[i] = True

                    # пункт 3.2: полные столбцы с учетом пропусков по границам
                    if sum(self.rows[i]) + (len(self.rows[i]) - 1) + biasLeft + biasRight == self.width:
                        offset = biasLeft
                        for k in range(len(self.rows[i])):
                            pos = 0
                            while True:
                                pos += 1
                                if pos > self.rows[i][k]:
                                    break
                                self.solution[i][offset] = Status.black
                                offset += 1
                            if k != len(self.rows[i]) - 1:
                                self.solution[i][offset] = Status.cross
                                offset += 1
                        self.filledRows[i] = True

                    # пункт 4: столбцы с неотмеченными границами закрашенных блоков и незакрашенных блоков по периметру
                    if self.solution[i][0] == Status.black:
                        j = 0
                        while j < self.rows[i][0]:
                            if self.solution[i][j] == Status.cross:
                                break
                            if self.solution[i][j] != Status.black:
                                self.solution[i][j] = Status.black
                            j += 1
                        if self.solution[i][j] == Status.white:
                            self.solution[i][j] = Status.cross
                        self.rowsValuesStatus[i][0] = True
                    if self.solution[i][self.width - 1] == Status.black:
                        j = self.width - 1
                        len_ = self.rows[i][len(self.rows[i]) - 1]
                        while j >= 0:
                            if len_ == 0 or self.solution[i][j] == Status.cross:
                                break
                            if self.solution[i][j] != Status.black:
                                self.solution[i][j] = Status.black
                            len_ -= 1
                            j -= 1
                        if self.solution[i][self.width - self.rows[i][len(self.rows[i]) - 1] - 1] == Status.white:
                            self.solution[i][self.width - self.rows[i][len(self.rows[i]) - 1] - 1] = Status.cross
                        self.rowsValuesStatus[i][len(self.rowsValuesStatus[i]) - 1] = True
                    if self.filledRows[i]:
                        self.rowsValuesStatus[i] = [True] * len(self.rowsValuesStatus[i])

                    # пункт 3.2.1: полные столбцы, имеющие закрашенные клетки по границам
                    if len(self.rows[i]) < 3 and (self.solution[i][0] == Status.black or self.solution[i][self.width - 1] == Status.black):
                        if len(self.rows[i]) == 2 and (
                                self.solution[i][0] != Status.black or self.solution[i][self.width - 1] != Status.black):
                            continue
                        if self.solution[i][0] == Status.black:
                            j = 0
                            while j < self.rows[i][0]:
                                if self.solution[i][j] == Status.cross:
                                    break
                                if self.solution[i][j] != Status.black:
                                    self.solution[i][j] = Status.black
                                j += 1

                        if self.solution[i][self.width - 1] == Status.black:
                            j = self.width - 1
                            length = self.rows[i][len(self.rows[i]) - 1]
                            while j >= 0:
                                if length == 0 or self.solution[i][j] == Status.cross:
                                    break
                                if self.solution[i][j] != Status.black:
                                    self.solution[i][j] = Status.black
                                length -= 1
                                j -= 1

                        for j in range(self.rows[i][0], self.width - self.rows[i][len(self.rows[i]) - 1]):
                            self.solution[i][j] = Status.cross
                        self.filledRows[i] = True

                if copySolution != self.solution:
                    affectedLines.append(1)

            if len(affectedLines) == 0:
                break

        # финальная обработка пазла с помощью SAT-решателя

    def solve(self):
        self.rows = [[0, 0, 0, 4, 2, 13], [0, 0, 0, 0, 10, 6], [0, 0, 5, 2, 8, 4], [0, 0, 0, 3, 9, 3], [0, 0, 3, 4, 5, 2], [0, 0, 2, 6, 3, 1], [0, 0, 0, 2, 8, 3], [0, 0, 5, 2, 3, 3], [0, 0, 0, 9, 2, 3], [0, 0, 5, 1, 2, 2], [0, 0, 3, 1, 2, 2], [0, 0, 3, 1, 2, 2], [0, 0, 2, 1, 2, 2], [0, 0, 1, 2, 1, 2], [0, 0, 2, 2, 1, 2], [0, 2, 1, 2, 2, 2], [0, 2, 1, 3, 2, 2], [2, 2, 1, 1, 2, 2], [0, 2, 2, 1, 2, 4], [0, 0, 2, 2, 1, 3], [0, 0, 0, 0, 3, 16], [0, 0, 0, 3, 4, 5], [0, 0, 0, 0, 6, 13], [0, 0, 0, 3, 6, 3], [0, 0, 0, 1, 2, 2], [0, 0, 0, 1, 2, 2], [0, 0, 0, 2, 2, 2], [0, 0, 2, 1, 2, 3], [0, 0, 0, 0, 10, 3], [0, 0, 0, 0, 5, 3]]
        self.cols = [[0, 0, 0, 0, 0, 6], [0, 0, 0, 0, 4, 5], [0, 0, 0, 0, 4, 4], [0, 0, 0, 0, 4, 3], [0, 0, 0, 0, 3, 3], [0, 0, 0, 0, 6, 2], [0, 0, 0, 0, 7, 5], [0, 0, 4, 2, 2, 3], [0, 0, 3, 1, 3, 3], [0, 0, 3, 8, 3, 2], [0, 3, 3, 5, 2, 2], [0, 2, 2, 2, 3, 2], [2, 2, 1, 1, 1, 2], [0, 2, 2, 1, 1, 1], [0, 3, 2, 1, 2, 2], [0, 2, 2, 1, 2, 1], [0, 2, 4, 1, 2, 2], [0, 1, 3, 2, 6, 6], [0, 1, 3, 2, 2, 8], [0, 1, 3, 2, 3, 4], [0, 0, 1, 2, 2, 5], [0, 0, 1, 2, 2, 3], [0, 0, 1, 3, 2, 5], [0, 0, 1, 3, 9, 2], [0, 0, 2, 2, 6, 3], [0, 0, 2, 3, 1, 4], [0, 0, 3, 4, 2, 3], [0, 0, 4, 4, 3, 3], [0, 0, 0, 5, 11, 2], [0, 0, 0, 6, 7, 1]]
        self.height = 30
        self.width = 30

        a = time.time()
        instance = Minisat22()
        compteur = self.width * self.height + 1

        # строки
        for i, c in enumerate(self.rows):
            lines = []
            for config in self.convert(self.height, c):
                x = list(range(i * self.height + 1, (i+1) * self.height +1))
                for v in [a * b for a, b in zip(x, config)]:
                    instance.add_clause([-compteur, v])
                    # print([-compteur, v], end="")
                lines.append(compteur)
                compteur += 1
            # print(lines)
            instance.add_clause(lines)
        # колонки
        for i, c in enumerate(self.cols):
            lines = []
            for config in self.convert(self.width, c):
                x = [i % self.height + self.height * j + 1 for j in range(self.height)]
                for v in [a * b for a, b in zip(x, config)]:
                    instance.add_clause([-compteur, v])
                    # print([-compteur, v], end="")
                lines.append(compteur)
                compteur += 1
            # print(lines)
            instance.add_clause(lines)

        print(time.time() - a)
        a = time.time()
        solvable = instance.solve()
        print(time.time() - a)

        if solvable:
            return instance.get_model()
        return None
