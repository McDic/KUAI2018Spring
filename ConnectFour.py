import math
import copy
import time
import random

def boardResult(board):  # True or False, otherwise None
    d = ((1, 0), (1, 1), (0, 1), (-1, 1))
    # d = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
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

def boardColumnAnalyze(board): # Return board analyzation by column
    d = ((1, 0), (1, 1), (0, 1), (-1, 1))
    # d = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
    result = {"full": [], True: [], False: [], None: []}
    for col in range(ConnectFour.maxCol):
        row = ConnectFour.maxRow - 1
        while row >= 0 and board[col][row] is None:
            row -= 1
        row += 1
        if row == ConnectFour.maxRow:
            result["full"].append(col)
        elif board[col][row] is None:
            x, y = col, row
            for targetTurn in (True, False):
                for dx, dy in d:
                    tempLen = 1
                    for i in range(1, ConnectFour.winLength):
                        x_, y_ = x + i*dx, y + i*dy
                        if x_ in range(ConnectFour.maxCol) and y_ in range(ConnectFour.maxRow):
                            if board[x_][y_] is not targetTurn:
                                break
                        else:
                            break
                        tempLen += 1
                    for i in range(1, ConnectFour.winLength):
                        x_, y_ = x - i*dx, y - i*dy
                        if x_ in range(ConnectFour.maxCol) and y_ in range(ConnectFour.maxRow):
                            if board[x_][y_] is not targetTurn:
                                break
                        else:
                            break
                        tempLen += 1
                    if tempLen >= ConnectFour.winLength and col not in result[targetTurn]:
                        result[targetTurn].append(col)
        if col not in result[True] and col not in result[False] and col not in result["full"]:
            result[None].append(col)
    return result

def boardPutted(board, col, turn):
    newboard = copy.deepcopy(board)
    if newboard[col][-1] is not None:
        raise IndexError("Already ful-filled column")
    h = len(newboard[col]) - 1
    while newboard[col][h] is None and h >= 0:
        h -= 1
    h += 1
    newboard[col][h] = turn
    return newboard

def boardPut(board, col, turn):
    if board[col][-1] is not None:
        raise IndexError("Already ful-filled column")
    h = len(board[col]) - 1
    while board[col][h] is None and h >= 0:
        h -= 1
    h += 1
    board[col][h] = turn

def boardStr(board):
    s = []
    for row in range(ConnectFour.maxRow-1, -1, -1):
        s.append(("%d:" % (row,)) + " ".join(ConnectFour.turnString[board[col][row]] for col in range(ConnectFour.maxCol)))
    return "\n".join(s)

class ConnectFour:

    maxRow = 6
    maxCol = 7
    winLength = 4
    defaultBiasFactor = math.sqrt(2)
    columnPriority = [0, 1, 2, 3, 2, 1, 0]
    # UCTsortKey = lambda p: (p[0], ConnectFour.columnPriority[p[1]])
    turnString = {None: "-", True: "O", False: "X"}

    # -------------------------------------------------------------------------
    # Primitive Function

    def __init__(self, col, turn, parent = None): # Put (col, turn) from parent node
        self.childs = [None] * ConnectFour.maxCol
        self.parent = parent
        self.col = col
        self.turn = turn

        self.simul_total = 0
        self.simul_win = 0
        self.simul_lose = 0
        
        if parent is None:
            self.board = [[None]*ConnectFour.maxRow for i in range(ConnectFour.maxCol)]
            if col is not None:
                self.board[col][0] = self.turn
        else:
            if self.parent.turn is self.turn:
                raise ValueError("Parent turn and self turn is same")
            elif col is None:
                raise ValueError("None turn cannot be on non-root node")
            elif self.parent.childs[col] is not None:
                raise KeyError("Already child exists")
            else:
                self.parent.childs[col] = self
            self.board = self.parent.put(col, self.turn)

        self.expanded = False

    def str_UCT(self):
        UCT = self.UCT()
        return "UCT = %s (Win %d, Lose %d / Total %d)" % (str(UCT), self.simul_win, self.simul_lose, self.simul_total)

    def str_childsUCT(self):
        s = []
        for col in range(ConnectFour.maxCol):
            if self.childs[col] is not None:
                s.append("Child #%d %s" % (col, self.childs[col].str_UCT()))
        return "\n".join(s)

    def __str__(self):
        s = []
        s.append("-"*50)
        s.append("Board ID: %d" % (id(self),))
        if self.parent is not None:
            s[-1] += " (Parent ID: %d)" % (id(self.parent),)
        if self.col is not None:
            s.append("Last placed with %s's turn at column %d" % (ConnectFour.turnString[self.turn], self.col))
        else:
            s.append("Initial board")
        s.append(self.str_UCT())
        if self.childs != [None] * ConnectFour.maxCol:
            s.append(self.str_childsUCT())
        s.append("")
        s.append(boardStr(self.board))
        s.append("")
        return "\n".join(s)

    # -------------------------------------------------------------------------
    # Basic Functions: Put new on board, Check result, etc.

    def put(self, col, turn):
        return boardPutted(self.board, col, turn)

    def result(self):
        return boardResult(self.board)

    def root(self):
        temp = self
        while temp.parent is not None:
            temp = temp.parent
        return temp

    def track(self, furthermoves):
        s = ""
        temp = self
        for futuremove in furthermoves:
            # print("MOVE %d" % futuremove)
            if temp is None:
                break
            s += str(temp)
            temp = temp.childs[futuremove]
        return s

    def backtrack(self):
        moveHistory = []
        temp = self
        while temp is not None:
            moveHistory.append(temp.col)
            temp = temp.parent
        moveHistory.pop()
        moveHistory.reverse()
        print("Backtrack for ID %d -> MoveHistory: %s" % (id(self), str(moveHistory)))
        return self.root().track(moveHistory)

    # -------------------------------------------------------------------------
    # Rule value

    def rule(self, firstTurn = False):
        if not firstTurn:
            analyze = boardColumnAnalyze(self.board)
            if analyze[not self.turn]:
                return analyze[not self.turn][0]
            elif analyze[self.turn]:
                return analyze[self.turn][0]
            else:
                height = []
                for i in range(ConnectFour.maxCol):
                    height.append(ConnectFour.maxRow - 1)
                    while self.board[i][height[i]] is None and height[i] >= 0:
                        height[i] -= 1
                    height[i] += 1

                for i in range(ConnectFour.maxCol - 3): # -XX-
                    if height[i+3] - height[i] in (0, 3, -3):
                        b = tuple(self.board[i+j][height[i]+j*(height[i+3] - height[i])//3] for j in range(4))
                        if b == (None, self.turn, self.turn, None):
                            return random.choice([i, i+3])

                for i in range(ConnectFour.maxCol - 2): # -XX-
                    if height[i+2] - height[i] in (0, 2, -2):
                        b = tuple(self.board[i+j][height[i]+j*(height[i+2] - height[i])//2] for j in range(3))
                        if b == (self.turn, None, self.turn):
                            return i+1

                if self.col not in analyze["full"]: # Same column as previous
                    return self.col

                maxMyHeight = -1
                maxMyCol = None
                for col in range(ConnectFour.maxCol): # Select highest
                    if col not in analyze["full"]:
                        row = 0
                        for row in range(height[col]-1, -1, -1):
                            if self.board[col][row] == (not self.turn):
                                break
                        if row > maxMyHeight:
                            maxMyHeight = row
                            maxMyCol = col
                return maxMyCol

        else:
            return 2

    # -------------------------------------------------------------------------
    # MonteCarlo UCT

    def UCT(self, C = defaultBiasFactor):
        t = self.root().simul_total
        if t == 0:
            return -math.inf
        elif self.simul_total == 0:
            return math.inf
        else:
            return self.simul_win/self.simul_total + C * math.sqrt(math.log(t, math.e) / self.simul_total)

    def maxUCTChild(self, C = defaultBiasFactor):
        UCTs = []
        for i in range(ConnectFour.maxCol):
            if self.childs[i] is not None:
                UCTs.append((self.childs[i].UCT(C = C), ConnectFour.columnPriority[i], i))
        UCTs.sort()
        return UCTs[-1]

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

    def simulation_pure(self, printing = False):
        board = copy.deepcopy(self.board)
        tempTurn = not self.turn
        while boardResult(board) is None:
            cols = []
            analyze = boardColumnAnalyze(board)
            if len(analyze[tempTurn]):
                cols = analyze[tempTurn]
            elif len(analyze[not tempTurn]):
                cols = analyze[not tempTurn]
            else:
                cols = analyze[None]
            if len(cols) == 0:
                return None
            nextCol = random.choice(cols)
            # print("At turn %s, choose column %d from %s\n\t(Analyze = %s)" % (ConnectFour.turnString[tempTurn], nextCol, str(cols), str(analyze)))
            boardPut(board, nextCol, tempTurn)
            tempTurn = not tempTurn
        # print("Simulate Result:")
        # print(boardStr(board))
        # print("*"*30)
        return boardResult(board)

    def simulResultUpdate(self, winCount, totalCount, loseCount):
        self.simul_win += winCount
        self.simul_total += totalCount
        self.simul_lose += loseCount
        if self.parent is not None:
            self.parent.simulResultUpdate(winCount, totalCount, loseCount)

    # -------------------------------------------------------------------------
    # MonteCarlo MainFunc

    def selection(self, firstTurn = False):
        if not firstTurn:
            self.expand()
            self.simulation(not self.turn)
            return self.maxUCTChild(C=0)[-1]
        else: # First Turn Restriction
            return 2

    def simulation(self, targetTurn, maxOverTime = 10):
        simulated = 0
        startedTime = time.time()
        simulated_total = 0
        simulated_win = 0
        simulated_lose = 0
        while time.time() - startedTime < maxOverTime:
            simulated += 1
            maxUCT = self.maxUCTChild()
            # print("Child %d Selected (UCT = %s)" % (maxUCT[-1], str(maxUCT[0])))
            # print(self.childs[maxUCT[-1]])
            pureSimulationResult = self.childs[maxUCT[-1]].simulation_pure()
            if pureSimulationResult is targetTurn:
                simulated_win = 1
                simulated_lose = 0
            elif pureSimulationResult is (not targetTurn):
                simulated_win = 0
                simulated_lose = 1
            else:
                simulated_win = 0
                simulated_lose = 0
            simulated_total = 1
            self.childs[maxUCT[-1]].simulResultUpdate(simulated_win, simulated_total, simulated_lose)
        print("\n%d times simulated in %.2f seconds" % (simulated, time.time() - startedTime))

def play():

    startCol = input("Input column number to start your turn first.\nIf you don't enter anything then I will start first: ")
    node = ConnectFour(int(startCol), False) if startCol.isdigit() else ConnectFour(None, False)
    firstTurn = not startCol.isdigit()
    print(node)
    turn = True

    while node.result() is None:
        
        node.expand()

        mode = input("""Input the mode(case insensitive). 
'MonteCarlo' or 'MC' for Monte Carlo search, 
'Rule' or 'R' for rule value, 
0~6 for column locating.
Your mode: """)

        if mode.lower() in ('montecarlo', 'mc'):
            if not turn:
                print("\nIt's not my turn, why you want to do MonteCarlo search? Input again.")
                continue
            nextCol = node.selection(firstTurn)
            node = node.childs[nextCol]
        elif mode.lower() in ('rule', 'r'):
            if not turn:
                print("\nIt's not my turn, why you want to use rule? Input again.")
                continue
            nextCol = node.rule(firstTurn)
            node = node.childs[nextCol]

        elif mode.isdigit():
            mode = int(mode)
            if mode not in range(ConnectFour.maxCol):
                print("\nInvalid column number. Input again.")
                continue
            elif node.board[mode][-1] is not None:
                print("\nAlready full-filled column. Input again.")
                continue
            elif input("""ARE YOU SURE TO PUT ON COLUMN %d? 
IF YES, THEN WRITE 'YES' AND PRESS ENTER, OTHERWISE JUST ENTER: """ % (mode,)).lower() != "yes":
                print("Ok, you rejected your input. Input again.")
                continue
            else:
                node = node.childs[mode]
        else:
            print("\nWrong mode, input again.")
            continue

        turn = not turn
        if node.parent is not None:
            print("\nColumn %d selected:" % (nextCol,))
            print(node.parent.str_childsUCT())
        print(node)

        if firstTurn:
            firstTurn = False

    print("%s WIN\n\n" % (ConnectFour.turnString[node.result()],))
    return node

if __name__ == "__main__":
    last_node = play()
    #print(last_node.backtrack())
