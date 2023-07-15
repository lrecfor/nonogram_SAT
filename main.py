from nonogram import Nonogram
import time

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    n = Nonogram()
    # n.calcSolution()
    # n.printNonogram(n.solution)
    a = time.time()
    res = n.solve()
    print(time.time() - a)
    for i in range(n.width * n.height):
        if res[i] < 0:
            print("", "   ", end="")
        else:
            print("*", "   ", end="")
        if i != 0 and i % n.width == 0:
            print("\n")
    # print(n.solve())
