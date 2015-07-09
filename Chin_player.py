import random, memory, constants

class MyPlayer:
    #this must always be even
    target = 4
    cut = 4

    def __init__(self, color):
        '''
        Make sure to store the color of your player ('B' or 'W')
        You may init your data structures here, if any
        '''
        print 'RandomPlayer init!' #print name of class to ensure that right class is used
        self.color = color #color is 'B' or 'W'

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
        memUsedMB = memory.getMemoryUsedMB()
        if memUsedMB > constants.MEMORY_LIMIT_MB - 100: #If I am close to memory limit
            #don't allocate memory, limit search depth, etc.
            #RandomPlayer uses very memory so it does nothing
            pass
               
        dirs = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
        corners = [(0,0),(0,7),(7,0),(7,7)]
        color = self.color
        if   color == 'W': oppColor = 'B'
        elif color == 'B': oppColor = 'W'
        else: assert False, 'ERROR: Current player is not W or B!'

        moves = []
        for i in xrange(len(board)):
            for j in xrange(len(board[i])):
                if board[i][j] != 'G': continue #background is green, i.e., empty square
                for ddir in dirs:
                    if self.validMove(board, (i,j), ddir, color, oppColor):
                        moves.append((i,j))
                        break
        for move in moves:
            if move in corners:
                return move

        return self.recurse(board,0,"max",color,oppColor,dirs)

    def recurse(self,board,depth,maxmin,me,opp,dirs):
        if depth == self.target:
            return self.naiveEval(board,me)

        if maxmin == "max":
            color = me
            oppColor = opp
        else:
            color = opp
            oppColor = me

        moves = []
        for i in xrange(len(board)):
            for j in xrange(len(board[i])):
                if board[i][j] != 'G': continue #background is green, i.e., empty square
                for ddir in dirs:
                    if self.validMove(board, (i,j), ddir, color, oppColor):
                        moves.append((i,j))
                        break
        maxminlist = []
        maxmindict = {}
        for move in moves:
            board[move[0]][move[1]] = color
            maxmin = "max" if maxmin == "min" else "min"
            val = self.recurse(board,depth+1,maxmin,me,opp,dirs)
            maxminlist.append(val)
            if depth==0:
                maxmindict[val] = move
            board[move[0]][move[1]] = 'G'
        if depth == 0:
            print maxminlist,maxmindict,maxmindict[max(maxminlist)]
            return maxmindict[max(maxminlist)] if len(maxminlist)!=0 else None

        if len(maxminlist)==0:
            val = 1000 if maxmin == "max" else -1000
            return val
        else:
            return max(maxminlist)
        
        




    def gameEnd(self, board):
        '''
        This is called when the game has ended.
        Add clean-up code here, if necessary.
        board is a copy of the end-game board configuration.
        '''
        # no clean up necessary for random player
        pass

    def getColor(self):
        '''
        Returns the color of the player
        '''
        return self.color
    
    def getMemoryUsedMB(self):
        '''
        You do not need to add to this code. Simply have it return 0
        '''
        return 0.0

    ########################### SUPPORT CODE #############################

    def validMove(self, board, pos, ddir, color, oppColor):
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

    def naiveEval(self,board,color):
        count = 0
        for i in xrange(len(board)):
            for j in xrange(len(board[i])):
                if board[i][j] == color:
                    count+=1
        return count
