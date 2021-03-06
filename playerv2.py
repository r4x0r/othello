# Import necessary modules
import random, memory, constants, copy

class Player:

  def __init__(self, color):
    '''
    Make sure to store the color of your player ('B' or 'W')
    You may init your data structures here, if any
    '''
    print 'OthelloPlayer init!' #print name of class to ensure that right class is used
    self.myColor = color #color is 'B' or 'W'

    # Constants to start with
    # Depth for the maximum value for the minimax to search to
    # Initialise the best value at the start. A negative value at the start.
    self.depth = 4
    self.bestValue = -100

    self.alpha = -100
    self.beta = 100

    # Initilise the opponent colour
    if color == 'W':
      self.oppoColor = 'B'

    else:
      self.oppoColor = 'W'


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

    # Check for the memory

    memUsedMB = memory.getMemoryUsedMB()
    if memUsedMB > constants.MEMORY_LIMIT_MB - 100:
      #If I am close to memory limit
      #don't allocate memory, limit search depth, etc.
      #RandomPlayer uses very memory so it does nothing
      print "Over memory limit, please alter!"


    # dirs = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)) # same as the dirs in constants.py
    # color = self.myColor
    # if   color == 'W': oppColor = 'B'
    # elif color == 'B': oppColor = 'W'
    # else: assert False, 'ERROR: Current player is not W or B!'

    # This is from random player
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

    # Use minimax to get best move
    bestMove = moves[0]
    bestValue = self.bestValue

    for move in moves:
      # you are a max player
      value = self.max_value(board, move, self.depth, self.alpha, self.beta)
      print "  M, V:", move, value
      if value > bestValue:
        bestValue = value
        bestMove = move

      print bestMove
      return bestMove


  def max_value(self, board, pos, depth, alpha, beta):
    """
    This function returns a utility value

    board: a list to represent all 64 squares
    pos: coordinates of position to explore
    depth: the depth of which the algo should recurse to. (to check for terminal)

    alpha and beta is used for alpha beta pruning
    alpha: for max value
    beta: for min value
    """

    # Check for terminal state
    if depth == 0:
      return self.evalkyn(board)
      #return eva_utility(board) # have to code the evaluation function

    # Copy the board to not screw it up
    boardCopy = copy.deepcopy(board)

    # Bestvalue
    bestValue = self.bestValue

    # Alpha Beta value
    alpha_value = alpha
    beta_value = beta

    # Find the valid moves
    valid_moves = self.find_valid_moves(boardCopy)
    # if there is no valid moves, sometimes there are no valid moves
    if len(valid_moves) == 0:
      print "evaluated at depth, by", depth, myColor
      return sign * self.evaluate_end(boardCopy)

    for move in valid_moves:
      value = self.min_value(boardCopy, move, depth -1, alpha_value, beta_value)
      bestValue = max(bestValue, value)

      # pruning part
      if bestValue >= beta_value:
        print "best value above beta value"
        return bestValue

      # updating the best value
      alpha_value = max(alpha_value, value)

    return bestValue

  def min_value(self, board, pos, depth, alpha, beta):
    """
    This function returns a utility value

    board: a list to represent all 64 squares
    pos: coordinates of position to explore
    depth: the depth of which the algo should recurse to. (to check for terminal)
    """
    # Check for terminal state
    if depth == 0:
      # return eva_utility(board) # have to code the evaluation function
      return self.evalkyn(board)

    # Copy the board to not screw it up
    boardCopy = copy.deepcopy(board)

    # Bestvalue
    bestValue = -1* self.bestValue

    # Alpha Beta value
    alpha_value = alpha
    beta_value = beta

    # Find the valid moves
    valid_moves = self.find_valid_moves(boardCopy)
    # if there is no valid moves, sometimes there are no valid moves
    if len(valid_moves) == 0:
      print "evaluated at depth, by", depth, myColor
      return sign * self.evaluate_end(boardCopy)

    for move in valid_moves:
      value = self.max_value(boardCopy, move, depth -1, alpha_value, beta_value)
      bestValue = min(bestValue, value)

      # pruning part
      if bestValue <= alpha_value:
        print "best value below alpha value"
        return bestValue

      # updating the best value
      beta_value = min(beta_value, value)

    return bestValue

#################### Evaluation and Heuristic Functions #########################

  def get_corners(self):
    size = constants.BRD_SIZE
    corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
    return corners

  def evaluate_white(self, board):
    # print "am called", color
    score = 0
    corners = self.get_corners()

    if board[3][3] == 'W':
      score += 2
    if board[4][3] == 'W':
      score += 2
    if board[3][4] == 'W':
      score += 2
    if board[4][4] == 'W':
      score += 2


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

  def evaluate_inside(self,board):
    score = 0
    if board[3][3] == "W":
      score += 1
    if board[4][3] == "W":
      score += 2
    if board[3][4] == "W":
      score += 2
    if board[4][4] == "W":
      score += 3
    return score

  def evalkyn(self,board):
  	#first determine game state

  	totalScore = 0
  	earlyScore = 0
  	lateScore = 0
  	my_discCount = count_white(self,board)
  	opponent_discCount = count_black(self,board)
  	corners = self.get_corners()

  	countGreen = count_empty(self,board)
  	state = 0 #0 for early game. 1 for mid-end game
  	if countGreen < 48:
  		state = 1

  	if state == 0: # early game, maintain fewer discs than opponent
  		if my_discCount < opponent_discCount:
  			earlyScore += 10
  		else: 
  			earlyScore -= 5

  	elif state == 1:
  		for corner in corners:
        	row, col = corner
        	# print board[row][col], "color"
        	if board[row][col] == 'W':
            	lateScore += 10
        	elif board[row][col] == 'G':
            	lateScore += 3
        	else:
            	lateScore -= 1
    totalScore = earlyScore + lateScore
    return totalScore






  def evaluate_end(self, board):
    score = 0
    for row in board:
        for sq in row:
            if sq  == 'W':
                score += 1
        print "    ", row
    print "    score", score
    return score


  def evaluate(self, board, color):
    print "am called", color
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

  #################### Used by the whole Othello programm ######################

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


  def find_valid_moves(self,board):
    """
    Returns a list of all the valid moves given a certain board configuration
    """
    moves = []
    for i in xrange(len(board)):
      for j in xrange(len(board[i])):
        if board[i][j] != 'G': continue #background is green, i.e., empty square
        for ddir in constants.DIRECTIONS:
          if self.validMove(board, (i,j), ddir, self.myColor, self.oppoColor):
            moves.append((i,j))
            break
    return moves

  def count_white(self,board):
  	count = 0
  	for i in xrange(7):
  		for j in xrange(7):
  			if board[i][j] == "W":
  				count += 1
  	return count

  def count_black(self,board):
  	count = 0
  	for i in xrange(7):
  		for j in xrange(7):
  			if board[i][j] == 'B'
  			count += 1
  	return count

  def count_empty(self,board):
  	count = 0
  	for i in xrange(7):
  		for j in xrange(7):
  			if board[i][j] == "G":
  				count += 1
  	return count
