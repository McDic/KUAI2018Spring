import math
import copy
import time
import random

def boardResult(board):  # True or False, otherwise None
    d = ((1, 0), (1, 1), (0, 1), (-1, 1))
    for x in range(ConnectFour.maxCol):
        for y in range(ConnectFour.maxRow):
            if board[x][y] is not None:
                for dx, dy in d:
                    tempStatus = True
                    for i in range(1, ConnectFour.winLength):
                        x_, y_ = x + i * dx, y + i * dy
                        if x_ in range(ConnectFour.maxCol) and y_ in range(ConnectFour.maxRow):
                            if board[x_][y_] != board[x][y]:
                                tempStatus = False
                                break
                        else:
                            tempStatus = False
                            break
                    if tempStatus:
                        return board[x][y]
    return None

def boardPut(board, col, turn):
    newboard = copy.deepcopy(board)
    if newboard[col][-1] is not None:
        raise IndexError("Already ful-filled column")
    h = len(newboard[col]) - 1
    while newboard[col][h] is None and h >= 0:
        h -= 1
    h += 1
    newboard[col][h] = turn
    return newboard


class ConnectFour:

    maxRow = 6
    maxCol = 7
    winLength = 4
    defaultBiasFactor = math.sqrt(2)
    columnPriority = [0, 1, 2, 3, 2, 1, 0]
    UCTsortKey = lambda p: (p[0], ConnectFour.columnPriority[p[1]])

    # -------------------------------------------------------------------------
    # Initialization

    def __init__(self, col, turn, parent = None):
        self.childs = [None] * ConnectFour.maxRow
        self.parent = parent
        self.col = col
        self.turn = turn

        self.simul_total = 0
        self.simul_win = 0
        if parent is None:
            self.board = [[None]*ConnectFour.maxRow for i in range(ConnectFour.maxCol)]
            self.board[col][0] = self.turn
        else:
            if self.parent.turn is self.turn:
                raise ValueError("Parent turn and self turn is same")
            elif self.parent.childs[col] is not None:
                raise KeyError("Already child exists")
            else:
                self.parent.childs[col] = self
            self.board = self.parent.put(col, self.turn)

        self.expanded = False

    # -------------------------------------------------------------------------
    # Primitive Functions: Put new on board, Check result, etc.

    def put(self, col, turn):
        return boardPut(self.board, col, turn)

    def result(self):
        return boardResult(self.board)

    def root(self):
        temp = self
        while temp.parent is not None:
            temp = temp.parent
        return temp

    # -------------------------------------------------------------------------
    # MonteCarlo SubFunc

    def expand(self):
        if self.expanded:
            return
        for col in range(ConnectFour.maxCol):
            try:
                self.childs[col] = ConnectFour(col, not self.turn, self)
            except (IndexError,) as err:
                self.childs[col] = None
        self.expanded = True

    def simulation_pure(self):
        board = copy.deepcopy(self.board)
        tempTurn = not self.turn
        while boardResult(board) is None:
            cols = []
            for col in range(ConnectFour.maxCol):
                if board[col][-1] is None:
                    cols.append(col)
            if len(cols) == 0:
                return None
            nextCol = random.choice(cols)
            board = boardPut(board, nextCol, tempTurn)
            tempTurn = not tempTurn
        return boardResult(board)

    def UCT(self, C = defaultBiasFactor):
        t = self.root().simul_total
        if t == 0:
            return -math.inf
        elif self.simul_total == 0:
            return math.inf
        else:
            return self.simul_win/self.simul_total + C * math.sqrt(math.log(t, math.e) / self.simul_total)

    def maxUCTChild(self):
        UCTs = []
        for i in range(ConnectFour.maxCol):
            if self.childs[i] is not None:
                UCTs.append((self.childs[i].UCT(), i))
        UCTs.sort(key=ConnectFour.UCTsortKey)
        return UCTs[-1]

    def simulResultUpdate(self, winCount, totalCount):
        self.simul_win += winCount
        self.simul_total += totalCount
        if self.parent is not None:
            self.parent.simulResultUpdate(winCount, totalCount)

    # -------------------------------------------------------------------------
    # MonteCarlo MainFunc

    def selection(self):
        self.expand()
        self.simulation(not self.turn)
        maxUCT, maxUCTIndex = self.maxUCTChild()
        return maxUCTIndex

    def simulation(self, targetTurn, maxOverTime = 110):
        startedTime = time.time()
        simulated_total = 0
        simulated_win = 0
        while time.time() - startedTime < maxOverTime:
            pureSimulationResult = self.childs[self.maxUCTChild()[1]].simulation_pure()
            if pureSimulationResult == targetTurn:
                simulated_win += 1
            simulated_total += 1
        self.simulResultUpdate(simulated_win, simulated_total)


def play(first = True):

    pass

