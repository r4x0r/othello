import random, memory, constants, copy

class Player:

    def __init__(self, color):
        '''
        Make sure to store the color of your player ('B' or 'W')
        You may init your data structures here, if any
        '''
        print 'OthelloPlayer init!' #print name of class to ensure that right class is used
        self.myColor = color #color is 'B' or 'W'
        if color == 'W':
            self.oppoColor = 'B'
            self.mySign = 1
        else:
            self.oppoColor = 'W'
            self.mySign = -1
        

        self.depth = 13
        self.bestValue = -100


        # self.boundary = []
        # a = int (constants.BRD_SIZE / 2)
        # b = a-1
        # for i in xrange(a-2, a+2):
        #     for j in xrange(a-2, a+2):
        #         self.boundary.append((i, j))

        # self.boundary.remove((b, b))
        # self.boundary.remove((b, a))
        # self.boundary.remove((a, b))
        # self.boundary.remove((a, a))


    def chooseMove(self, board, prevMove):
        '''
        board is a two-dimensional list representing the current board configuration.
        board is a copy of the original game board, so you can do to it as you wish.
        board[i][j] is 'W', 'B', 'G' when row i and column j contains a
        white piece, black piece, or no piece respectively.
        As usual i, j starts from 0, and board[0][0] is the top-left corner.
        prevMove gives the i, j coordinates of the last move made by your opponent.
        prevMove[0] and prevMove[1] are the i and j-coordinates respectively.
        prevMove may be None if your opponent has no move to make during his last turn.
        '''  

        # ignore memory limit for now

        # memUsedMB = memory.getMemoryUsedMB()
        # if memUsedMB > constants.MEMORY_LIMIT_MB - 100: 
        #     #If I am close to memory limit
        #     #don't allocate memory, limit search depth, etc.
        #     #RandomPlayer uses very memory so it does nothing
        #     pass
        

        # dirs = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)) # same as the dirs in constants.py
        # color = self.color
        # if   color == 'W': oppColor = 'B'
        # elif color == 'B': oppColor = 'W'
        # else: assert False, 'ERROR: Current player is not W or B!'

        # find all valid moves
        moves = []
        for i in xrange(len(board)):
            for j in xrange(len(board[i])):
                if board[i][j] != 'G': continue #background is green, i.e., empty square
                for ddir in constants.DIRECTIONS:
                    if self.validMove(board, (i,j), ddir, self.myColor, self.oppoColor):
                        moves.append((i,j))
                        break
        if len(moves) == 0: return None #no valid moves

        # use negamax to decide
        bestMove = moves[0]
        bestValue = self.bestValue # * float('infinity')
        print self.myColor, "  choices:"
        for move in moves:
            value = self.negamax(board, move, self.depth, self.myColor, self.oppoColor, self.mySign)
            print "  M, V:", move, value
            if value > bestValue:
                bestValue = value
                bestMove = move
       
        # if bestMove == None: # due to the case when values are all -inf
        #     bestMove = moves[0]
        
        print "  best M, V:", bestMove, bestValue
        return bestMove 

    def negamax(self, board, pos, depth, myColor, oppoColor, sign): 
        """
        board: 2D list
        pos: coordinates of position to explore
        depth: depth to which negamax should search to (default depth is 1000)
        color: player's color
        dirs: list of directions of adjacents squares
        """
        if depth == 0: # or game.isGoal()
            return sign * self.evaluate_white(board) # color * heuristic value of node; possibly number of pieces on board 

        # oppColor = 'W'
        # if color == 'W':
        #     oppColor = 'B'

        boardCopy = copy.deepcopy(board)
        
        """
        flips = []
        self.board[node[0]][node[1]] = color

        for ddir in constants.DIRECTIONS:
            if self.validMove(boardCopy, (node[0], node[1]), ddir, oppoColor, myColor):
                newPos = (node[0]+ddir[0], node[1]+ddir[1])
                validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
                if not validPos: return False
                if board[newPos[0]][newPos[1]] != oppColor: return False
                
                while self.board[newPos[0]][newPos[1]] == oppColor:
                    self.board[newPos[0]][newPos[1]] = color
                    flips.append(newPos)
                    newPos = Board.addToPos(newPos, ddir)
        return flips
        """
        # I make a move
        boardCopy[pos[0]][pos[1]] = myColor

        # flip other pieces on the board
        for ddir in constants.DIRECTIONS:
            if self.validMove(boardCopy, pos, ddir, myColor, oppoColor):
                newPos = (pos[0] + ddir[0], pos[1] + ddir[1])
                while boardCopy[newPos[0]][newPos[1]] == oppoColor:
                    boardCopy[newPos[0]][newPos[1]] = myColor
                    newPos = (pos[0] + ddir[0], pos[1] + ddir[1])

        # flips all valid adjacent squares
        # for ddir in constants.DIRECTIONS:
        #     newPos = (node[0]+ddir[0], node[1]+ddir[1])
        #     validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
        #     if not validPos: return False
        #     if boardCopy[newPos[0]][newPos[1]] != oppColor: continue

        #     while boardCopy[newPos[0]][newPos[1]] == oppColor:
        #         boardCopy[newPos[0]][newPos[1]] = myColor
        #         newPos = (newPos[0]+ddir[0], newPos[1]+ddir[1])
        #         validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
        #         if not validPos: break

        # find all valid moves for oppo
        # MAKE THIS SHIT INTO FUNCTION
        moves = []
        for i in xrange(len(board)):
            for j in xrange(len(board[i])):
                if boardCopy[i][j] != 'G': continue #background is green, i.e., empty square
                for ddir in constants.DIRECTIONS:
                    if self.validMove(boardCopy, (i, j), ddir, oppoColor, myColor):
                        moves.append((i,j))
                        break

        # need to modify this in future, as there is a difference between endgame and trapped game
        if len(moves) == 0:
            # NEED TO MOVE AHEAD AND PLAY WHEN OPPONENT GETS STUCK
            print "evaluated at depth, by", depth, myColor
            return sign * self.evaluate_end(boardCopy)

        bestValue = self.bestValue # * float('infinity') # can change to a smaller value
        for move in moves:
            value = -1 * self.negamax(boardCopy, move, depth-1, oppoColor, myColor, -1*sign)
            bestValue = max(bestValue, value)
        return bestValue

    def get_corners(self):
        size = constants.BRD_SIZE
        corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
        return corners

    def evaluate_white(self, board):
        # print "am called", color
        score = 0
        corners = self.get_corners()

        for corner in corners:
            row, col = corner
            # print board[row][col], "color"
            if board[row][col] == 'W':
                score += 10
            elif board[row][col] == 'G':
                score += 3 
            else:
                score += 1
        return score

    def evaluate_end(self, board):
        score = 0
        for row in board:
            for sq in row:
                if sq  == 'W':
                    score += 1
            print "    ", row
        print "    score", score
        return score

        # w_score = 0
        # b_score = 0
        # w_corner = 0
        # b_corner = 0

        # # for row in board:
        # #     for sq in row:
        # #         if sq  == 'W':
        # #             score += 1
        # #         elif sq == 'B':
        # #             score -= 1
        # # return score

        # for row in board:
        #     for sq in row:
        #         if sq  == 'W':
        #             w_score += 1
        #         elif sq == 'B':
        #             b_score += 1

        # corners = self.get_corners()
        # for corner in corners:
        #     row, col = corner
        #     # print board[row][col], "color"
        #     if board[row][col] == 'W':
        #         w_corner += 1
        #     elif board[row][col] == 'B':
        #         b_corner += 1
        
        # if w_score > b_score:
        #     return 8 - b_corner
        # elif w_score < b_score: 
        #     return -8 + w_corner
        # return w_corner



    def evaluate(self, board, color):
        # print "am called", color
        score = 0
        corners = self.get_corners()

        for corner in corners:
            row, col = corner
            # print board[row][col], "color"
            if board[row][col] == color:
                score += 10
            elif board[row][col] == 'G':
                score += 5
        return score

    def gameEnd(self, board):
        '''
        This is called when the game has ended.
        Add clean-up code here, if necessary.
        board is a copy of the end-game board configuration.
        '''
        print "ended"
        return

    def getColor(self):
        '''
        Returns the color of the player
        '''
        return self.myColor
    
    def getMemoryUsedMB(self):
        '''
        You do not need to add to this code. Simply have it return 0
        '''
        return 0.0

    ########################### SUPPORT CODE #############################

    def validMove(self, board, pos, ddir, color, oppColor):
        """
        board: 2D list of lists
        pos: coordinate of the move in query
        ddir: taken from constants.py (to get the coordinates of all adjacent squares)
        color: color of current player
        oppColor: opponent's color

        newPos refers to an adjacent square of current node
        Checks whether any adjacent square of current node is occupied by opponent's piece
        Once an adjacent square that is occuped by the opponent is found, the search continues in that direction 
        until a piece of player's own color is found and returns True
        else returns False        
        """
        newPos = (pos[0]+ddir[0], pos[1]+ddir[1])
        validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
        if not validPos: return False
        if board[newPos[0]][newPos[1]] != oppColor: return False

        while board[newPos[0]][newPos[1]] == oppColor:
            newPos = (newPos[0]+ddir[0], newPos[1]+ddir[1])
            validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
            if not validPos: break

        validPos = newPos[0] >= 0 and newPos[0] < constants.BRD_SIZE and newPos[1] >= 0 and newPos[1] < constants.BRD_SIZE
        if validPos and board[newPos[0]][newPos[1]] == color:
            return True
        return False
