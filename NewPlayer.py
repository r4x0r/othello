import random, memory, constants, copy

##################################################################################
##################################################################################
########################## GAMESTATE (BITBOARD) ##################################
##################################################################################
##################################################################################
class BitBoard():

    def __init__(self):
        self.whole_length = 64
        self.unit_length = 8
        self.unit_max_value = 2**self.unit_length -1

        self.left_mask =  0x7F7F7F7F7F7F7F7F
        self.right_mask = 0xFEFEFEFEFEFEFEFE
        self.full_mask =  0xFFFFFFFFFFFFFFFF
        self.corners =    0x8100000000000081

        self.debruijn64magic =  0x07EDD5E59A4E28C2
        self.debruijn64transform = [63,  0, 58,  1, 59, 47, 53,  2,
                                    60, 39, 48, 27, 54, 33, 42,  3,
                                    61, 51, 37, 40, 49, 18, 28, 20,
                                    55, 30, 34, 11, 43, 14, 22,  4,
                                    62, 57, 46, 52, 38, 26, 32, 41,
                                    50, 36, 17, 19, 29, 10, 13, 21,
                                    56, 45, 25, 31, 35, 16,  9, 12,
                                    44, 24, 15,  8, 23,  7,  6,  5]

    ##-------------------------- Directions Functions ----------------------------
    def left(self, bitboard):
        return (bitboard >> 1) & self.left_mask
    def right(self, bitboard):
        return (bitboard << 1) & self.right_mask
    def up(self, bitboard):
        return bitboard >> 8
    def down(self, bitboard):
        return bitboard << 8
    def upleft(self, bitboard):
        return (bitboard >> 9) & self.left_mask
    def upright(self, bitboard):
        return (bitboard >> 7) & self.right_mask
    def downleft(self, bitboard):
        return (bitboard << 7) & self.left_mask
    def downright(self, bitboard):
        return (bitboard << 9) & self.right_mask


    ##---------------------- Get / Set(on clone) Functions for Bitboards ---------------
    def getAllPieces(self, playerBoard, opponentBoard):
        return playerBoard | opponentBoard

    def getEmptySquares(self, playerBoard, opponentBoard):
        allpieces = self.getAllPieces(playerBoard, opponentBoard)
        return allpieces ^ self.full_mask 

    def getDirValidPlay(self, dir_func, playerBoard, opponentBoard, emptySquares):
        shifted_player = dir_func(playerBoard)
        potential_flip = shifted_player & opponentBoard
        valid_play = 0
        while potential_flip > 0:
            # shift in same direction
            potential_flip = dir_func(potential_flip)
            # check if square empty i.e. play can be made
            valid_play = valid_play | (potential_flip & emptySquares)
            # if not, check if occupying piece is still a potential flip (opponent)
            potential_flip = potential_flip & opponentBoard
        return valid_play

    def getAllValidPlay(self, playerBoard, opponentBoard, emptySquares):
        return    self.getDirValidPlay(self.up, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.down, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.left, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.right, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.upleft, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.upright, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.downleft, playerBoard, opponentBoard, emptySquares) \
                | self.getDirValidPlay(self.downright, playerBoard, opponentBoard, emptySquares)

    def flipDir(self, dir_func, position, playerBoard, opponentBoard):
        potential_flip = dir_func(position)
        flipped = 0
        while potential_flip > 0:
            if (potential_flip & playerBoard) > 0:
                # reached own pieces in direction
                return flipped
            # pieces that can be flipped
            potential_flip = potential_flip & opponentBoard
            # store in flipped
            flipped = flipped | potential_flip
            # continue in the direction
            potential_flip = dir_func(potential_flip)
        return 0

    def flipAll(self, position, playerBoard, opponentBoard):
        return   self.flipDir(self.up, position, playerBoard, opponentBoard) \
               | self.flipDir(self.down, position, playerBoard, opponentBoard) \
               | self.flipDir(self.left, position, playerBoard, opponentBoard) \
               | self.flipDir(self.right, position, playerBoard, opponentBoard) \
               | self.flipDir(self.upleft, position, playerBoard, opponentBoard) \
               | self.flipDir(self.upright, position, playerBoard, opponentBoard) \
               | self.flipDir(self.downleft, position, playerBoard, opponentBoard) \
               | self.flipDir(self.downright, position, playerBoard, opponentBoard) 

    def newPlayerBoard(self, playerBoard, flipped, position):
        return playerBoard | flipped | position

    def newOpponentBoard(self, opponentBoard, flipped):
        return opponentBoard ^ flipped

    ##---------------------- Attributes Function (for Evaluation) --------------------
    def getNumBits(self, bitboard):
        """ uses SWAR-popcount method """
        k1 = 0x5555555555555555 # -1/3
        k2 = 0x3333333333333333 # -1/5
        k4 = 0x0f0f0f0f0f0f0f0f #  -1/17
        kf = 0x0101010101010101 #  -1/255

        bitboard = bitboard - ((bitboard >> 1) & k1)        # count per 2 bits
        bitboard = (bitboard & k2) + ((bitboard >> 2) & k2) # 4bit-sum of every pair of count
        bitboard = (bitboard + (bitboard >> 4)) & k4        # 8bit-sum of those sums
        bitboard = (bitboard * kf) >> 56                    # adding all 8bit-sums using multiplication, collect MSBs
        return bitboard & 0xFF

    def bitScanForward(self, bitboard):
        subset = bitboard & (-1 * bitboard)
        return self.debruijn64transform[((subset * self.debruijn64magic) >> 58) & 0x3F]

    def listIndex(self, bitboard):
        indices = []
        while bitboard > 0:
            index = self.bitScanForward(bitboard)
            indices.append(index)
            bitboard = bitboard ^ (1 << index)
        return indices

    def getDirFrontier(self, dir_func, opp_dir_func, bitboard, emptySquares):
        shifted_bitboard = dir_func(bitboard)
        shifted_bitboard = shifted_bitboard & emptySquares
        shifted_bitboard = opp_dir_func(shifted_bitboard)
        return shifted_bitboard * bitboard

    def getFrontier(self, bitboard, emptySquares):
        return   self.getDirFrontier(self.up, self.down, bitboard, emptySquares) \
               | self.getDirFrontier(self.down, self.up, bitboard, emptySquares) \
               | self.getDirFrontier(self.left, self.right, bitboard, emptySquares) \
               | self.getDirFrontier(self.right, self.left, bitboard, emptySquares) \
               | self.getDirFrontier(self.upleft, self.downright, bitboard, emptySquares) \
               | self.getDirFrontier(self.upright, self.downleft, bitboard, emptySquares) \
               | self.getDirFrontier(self.downleft, self.upright, bitboard, emptySquares) \
               | self.getDirFrontier(self.downright, self.upleft, bitboard, emptySquares) 

    def getCorners(self, bitboard):
        return bitboard & self.corners

    def exclude360(self, bitboard):
        return    self.left(bitboard) \
                | self.right(bitboard) \
                | self.up(bitboard) \
                | self.down(bitboard) \
                | self.upleft(bitboard) \
                | self.upright(bitboard) \
                | self.downleft(bitboard) \
                | self.downright(bitboard)

    ##--------------------------------- Support Function -----------------------------
    def testPrint(self):
        bitboard = 0x810000000
        print "original"
        self.printBitBoard(bitboard, 'B')
        print "\nleft"
        self.printBitBoard(self.left(bitboard), 'B')
        print "\nright"
        self.printBitBoard(self.right(bitboard), 'B')
        print "\nup"
        self.printBitBoard(self.up(bitboard), 'B')
        print "\ndown"
        self.printBitBoard(self.down(bitboard), 'B')
        print "\nupleft"
        self.printBitBoard(self.upleft(bitboard), 'B')
        print "\nupright"
        self.printBitBoard(self.upright(bitboard), 'B')
        print "\ndownleft"
        self.printBitBoard(self.downleft(bitboard), 'B')
        print "\ndownright"
        self.printBitBoard(self.downright(bitboard), 'B')
    
    def printBitBoard(self, bitboard, color):
        """
        lsb is top left corner
        i.e lsb = (0,0), next = (0,1), msb = (7,7) 
        """
        piece = 'X'
        if color == 'W':
            piece = 'O'

        length = 0
        while length < self.whole_length:
            current_word = self.unit_max_value & (bitboard >> length)
            string = ""

            count = 0
            while count < self.unit_length:
                current_bit = 1 & (current_word >> count)
                if current_bit > 0:
                    string += piece
                else:
                    string += '.'
                count += 1
            print string
            length += self.unit_length

    def printCombine(self, playerBoard, opponentBoard, color):
        white = playerBoard
        black = opponentBoard
        if color == 'B':
            white = opponentBoard
            black = playerBoard

        length = 0
        while length < self.whole_length:
            current_white = self.unit_max_value & (white >> length)
            current_black = self.unit_max_value & (black >> length)
            string = ""

            count = 0
            while count < self.unit_length:
                white_bit = 1 & (current_white >> count)
                black_bit = 1 & (current_black >> count)
                sq = '.'
                if white_bit > 0:
                    sq = 'O'
                if black_bit > 0:
                    sq = 'X'
                string += sq
                count += 1
            print string
            length += self.unit_length



##################################################################################
##################################################################################
#################################### PLAYER AGENT ################################
##################################################################################
##################################################################################
class Player:

    def __init__(self, color):
        '''
        Make sure to store the color of your player ('B' or 'W')
        You may init your data structures here, if any
        '''
        print 'smartAss-C3Q0 initialise!'
        # game state attributes
        self.gameState = BitBoard()
        self.color = color
        if color == 'W':
            self.oppColor = 'B'
        else:
            self.oppColor = 'W'
        self.mySign = 1
        self.progress = 0

        
        
        # search algo attributes
        self.bestValue = -157500
        self.alpha = -157500
        self.beta = 157500

        # heuristics attributes
        #   (number of empty spaces -1)
        self.depth = 5      # early game
        self.max_depth = 4  # for mid game
        self.early_game = 16 # games starts at progress = 4
        self.mid_game = 32
        self.late_game = 52 
        self.stabilityArray = [20, -3, 11,  8,  8, 11, -3, 20,
                               -3, -7, -4,  1,  1, -4, -7, -3,
                               11, -4,  2,  2,  2,  2, -4, 11,
                                8,  1,  2, -3, -3,  2,  1,  8, 
                                8,  1,  2, -3, -3,  2,  1,  8,
                               11, -4,  2,  2,  2,  2, -4, 11,
                               -3, -7, -4,  1,  1, -4, -7, -3,
                               20, -3, 11,  8,  8, 11, -3, 20]

        self.debruijnStability = self.generateDebruijnMapping(self.stabilityArray, self.gameState.debruijn64transform)
        # self.printStabilityTable()

        """
            ( 1000,    -1000)
            (80174,   -80172)
            (57303,   -57303)
            ( 7892,    -7892)
            ( 7439,    -7439)
            ( 3600,    -3600)
        =   (157410, -157408)
        """
        # Coefficients for early game
        # self.Cp = 10
        # self.Cc = 801.724
        # self.Ca = 382.026
        # self.Cm = 78.922
        # self.Cf = 74.396
        # self.Cs = 10

        self.Cp = 10
        self.Cc = 801.724
        self.Ca = 382.026
        self.Cm = 140.922
        self.Cf = 74.396
        self.Cs = 10


        # statistics
        self.expandedNodes = 0
        self.maxMem = 0
        self.globalMax = 0

    def chooseMove(self, board, prevMove):  
        # memUsedMB = memory.getMemoryUsedMB()
        # print "mem:", memUsedMB
        # if memUsedMB > constants.MEMORY_LIMIT_MB - 7: 
        #     print "MEMORY LIMIT ALERT usage", memUsedMB, "MB"

        currMB = self.matrixToBB(board, self.color)
        currOB = self.matrixToBB(board, self.oppColor)
        currEB = self.gameState.getEmptySquares(currMB, currOB)

        allPieces = self.gameState.getAllPieces(currMB, currOB)
        self.progress = self.gameState.getNumBits(allPieces)

        ## STRATEGY ##
        if self.progress <= self.early_game:
            if self.progress == 4:
                # first move of the game
                return (2, 4)
            elif self.progress == 5: 
                # if second player, use diagonal opening strategy
                if prevMove[0] < 4:
                    return (2, 5)
                else:
                    return (5, 2) 
        elif self.progress > self.early_game and self.progress <= self.mid_game:
            self.depth = self.max_depth
            # change the coefficient at early mid-game
            self.Cp = 200
            self.Cc = 801.724
            self.Ca = 382.026
            self.Cm = 200
            self.Cf = 50
            self.Cs = 10
        elif self.progress > self.mid_game and self.progress < self.late_game:
            # self.depth = self.max_depth
            # change the coefficient at late mid-game
            self.Cp = 400
            self.Cc = 801.724
            self.Ca = 192.026
            self.Cm = 200
            self.Cf = 10
            self.Cs = 10
        else:
            self.depth = 64 - self.late_game

        # find all valid moves
        moves = []
        validPosition = self.gameState.getAllValidPlay(currMB, currOB, currEB)
        if validPosition > 0:
            moves = self.gameState.listIndex(validPosition)
        if len(moves) == 0: 
            # print "!!!!!!!!!NO VALID MOVE!!!!!!!!"
            return None #no valid moves

        bestMove = 0
        bestValue = self.bestValue

        print self.color, "choosing move:"
        print "  progress", self.progress
        ####  START NEGASCOUT 
        alpha = self.alpha
        beta = self.beta
        alpha_move = None
        for move in moves:
            # make one move
            position = 1 << move
            flipped = self.gameState.flipAll(position, currMB, currOB)
            newMB = self.gameState.newPlayerBoard(currMB, flipped, position)
            newOB = self.gameState.newOpponentBoard(currOB, flipped)
            newEB = self.gameState.getEmptySquares(newMB, newOB)
            # call negascout
            value = -1 * self.negascoutBB(self.depth, newMB, newOB, newEB, -1*self.mySign, -1*beta, -1*alpha)
            # self.incrementNodes()
            # print "   M, V:", (move/8, move%8), value
            
            # search is now using piece difference evaluation
            if self.progress >= self.late_game:
                # as long as game can be won, return
                if value > 0:
                    print "     LATE GAME PRUNE", (move/8, move%8), value
                    # self.reportNodes()
                    # self.resetNodes()
                    return (move/8, move%8)

            if value > bestValue:
                bestValue = value
                bestMove = move
        ###  END NEGASCOUT 

        print "     best M, V:", (bestMove/8, bestMove%8), bestValue
        # self.reportNodes()
        # self.resetNodes()
        return (bestMove/8, bestMove%8)

    ##-------------------------- Adverserial Search Algorithm ----------------------
    def negascoutBB(self, depth, mB, oB, eB, sign, alpha, beta): 
        # memUsedMB = memory.getMemoryUsedMB()
        # if memUsedMB > constants.MEMORY_LIMIT_MB - 7: 
        #     print "MEMORY LIMIT ALERT usage", memUsedMB, "MB"
        #     depth = 0

        if depth == 0:
            return sign * self.evaluation_func(mB, oB, eB, sign)

        # find all valid moves for opponent
        moves = []
        validPosition = self.gameState.getAllValidPlay(oB, mB, eB)
        if validPosition > 0:
            moves = self.gameState.listIndex(validPosition)

        bestValue = self.bestValue
        # scores = []
        if len(moves) == 0:
            # opponent has no moves
            validPosition = self.gameState.getAllValidPlay(mB, oB, eB)
            if validPosition > 0:
                moves = self.gameState.listIndex(validPosition)
            if len(moves) == 0:
                # both ran out of moves
                bestValue = sign * self.evaluation_func(mB, oB, eB, sign)
            else:
                # maintained inverted attributes
                inv_alpha = -1*beta
                inv_beta = -1*alpha

                for move in moves:
                    # make a move
                    position = 1 << move
                    flipped = self.gameState.flipAll(position, mB, oB)
                    new_mB = self.gameState.newPlayerBoard(mB, flipped, position)
                    new_oB = self.gameState.newOpponentBoard(oB, flipped)
                    new_eB = self.gameState.getEmptySquares(new_mB, new_oB)
                    # inversion start, but alpha beta remained with current convention
                    value = -1*self.negascoutBB(depth-1, new_mB, new_oB, new_eB, sign, -1*inv_beta, -1*inv_alpha)
                    # self.incrementNodes()
                    # pruning
                    bestValue = max(bestValue, value)
                    if value > inv_alpha:
                        inv_alpha = value
                    if inv_beta < inv_alpha:
                        # inversion end
                        return -1*inv_alpha
                # inversion end
                bestValue = -1*bestValue
        else:
            for move in moves:
                position = 1 << move
                flipped = self.gameState.flipAll(position, oB, mB)
                new_oB = self.gameState.newPlayerBoard(oB, flipped, position)
                new_mB = self.gameState.newOpponentBoard(mB, flipped)
                new_eB = self.gameState.getEmptySquares(new_mB, new_oB)
                value = -1 * self.negascoutBB(depth-1, new_oB, new_mB, new_eB, -1*sign, -1*beta, -1*alpha)
                # self.incrementNodes()
                # pruning:
                bestValue = max(bestValue, value)
                if value > alpha:
                    alpha = value
                if beta < alpha:
                    return alpha
        return bestValue

    ##------------------------------ Nodes Tracker -------------------------------
    def incrementNodes(self):
        self.expandedNodes += 1

    def resetNodes(self):
        self.expandedNodes = 0
        if self.maxMem > self.globalMax:
            self.globalMax = self.maxMem
        self.maxMem = 0

    def reportNodes(self):
        # print "     Number of nodes expanded:", self.expandedNodes
        print "                     mem used:", self.maxMem

    ##------------------------------ Support Functions --------------------------
    def matrixToBB(self, matrix, color):
        bb = 0
        row = 7
        while row > -1:
            col = 7
            while col > -1:
                bb = bb << 1
                if matrix[row][col] == color:
                    bb += 1
                col -= 1
            row -= 1
        return bb

    def gameEnd(self, board):
        '''
        This is called when the game has ended.
        Add clean-up code here, if necessary.
        board is a copy of the end-game board configuration.
        '''
        print self.color, "has been terminated"
        # self.gameState.printBitBoard(self.myBoard, 'W')
        # print "global max memory", self.globalMax
        return

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

    ##-------------------------- Heuristic Functions -------------------------
    def generateDebruijnMapping(self, posVal, debruijnArray):
        debruijnPosVal = []
        for i in debruijnArray:
            debruijnPosVal.append(posVal[i])
        return debruijnPosVal

    def printStabilityTable(self):
        print "Debruijn Magic Array"
        count = 0
        for i in xrange(8):
            for j in xrange(8):
                if j < 7:
                    print self.gameState.debruijn64transform[count],
                else:
                    print self.gameState.debruijn64transform[count]
                count += 1
        print 
        print "Position Value Table"
        count = 0
        for i in xrange(8):
            for j in xrange(8):
                if j < 7:
                    print self.stabilityArray[count],
                else:
                    print self.stabilityArray[count]
                count += 1
        print 
        print "Debruijn Position Value Table"
        count = 0
        for i in xrange(8):
            for j in xrange(8):
                if j < 7:
                    print self.debruijnStability[count],
                else:
                    print self.debruijnStability[count]
                count += 1
        print

    def evaluation_func(self, myBoard, oppBoard, empty, sign):
        """
        weighted evaluation function = 10p + 801.724c + 382.026l + 78.922m + 74.396f + 10d
                                    (1000,    -1000)
                                    (80174.4, -80172.4)
                                    (57303.9, -57303.9)
                                    (7892.2,  -7892.2)
                                    (7439.6,  -7439.6)
                                    (3600,    -3600)
                                =   (157410.1, -157408.1)
        the above values are obtained from research done by University of Washington
        """
        # memUsedMB = memory.getMemoryUsedMB()
        # if memUsedMB > self.maxMem:
        #     self.maxMem = memUsedMB

        white = myBoard
        black = oppBoard
        if sign > 0:
            white = oppBoard
            black = myBoard

        num_white = self.gameState.getNumBits(white)
        num_black = self.gameState.getNumBits(black)
        score = num_white - num_black
        if num_white == 0:
            return -160000
        if num_black == 0:
            return 160000

        if self.progress < self.late_game:
            ratio_p = self.getPieceRatio(num_white, num_black)
            ratio_f  = self.getFrontierRatio(white, black, empty)
            val_s = 0 # self.getStability(white, black)
            val_c = self.getCorners(white, black)
            val_a = self.getCAdjacent(white, black, empty)
            ratio_m = self.getMobility(white, black, empty)
            
            # if self.progress < self.early_game:
            #     score = self.eCp*ratio_p + self.eCc*val_c + self.eCa*val_a + self.eCm*ratio_m + self.eCf*ratio_f + self.eCs*val_s
            # else:
            score = self.Cp*ratio_p + self.Cc*val_c + self.Ca*val_a + self.Cm*ratio_m + self.Cf*ratio_f + self.Cs*val_s
        return score

    def getPieceRatio(self, num_white, num_black):
        ratio_p = 0
        if num_white > num_black:
            ratio_p = (100.0 * num_white)/(num_white + num_black)
        elif num_white < num_black:
            ratio_p = (-1 * 100.0 * num_black)/(num_white + num_black)
        return ratio_p

    def getFrontierRatio(self, white, black, empty):
        ratio_f = 0
        white_val = 0
        black_val = 0

        white_front = self.gameState.getFrontier(white, empty)
        black_front = self.gameState.getFrontier(black, empty)
        if white_front > 0:
            white_val = self.gameState.getNumBits(white_front)
        if black_front > 0:
            black_val = self.gameState.getNumBits(black_front)

        if (white_val > black_val):
            ratio_f = (-1* 100.0 * white_val)/(white_val + black_val)
        elif (white_val < black_val):
            ratio_f = (100.0 * black_val)/(white_val + black_val)
        return ratio_f

    def getStability(self, white, black):
        val_s = 0
        while white > 0:
            index = self.gameState.bitScanForward(white)
            val_s += self.debruijnStability[index]
            white = white ^ (1 << index)
        while black > 0:
            index = self.gameState.bitScanForward(black)
            val_s -= self.debruijnStability[index]
            black = black ^ (1 << index)
        return val_s

    def getCAdjacent(self, white, black, empty):
        val_a = 0
        white_count = 0
        black_count = 0

        empty_corners = self.gameState.getCorners(empty)
        if empty_corners > 0:
            empty_adjacent = self.gameState.exclude360(empty_corners)
            white_adj = white | empty_adjacent
            black_adj = black | empty_adjacent
            if white_adj > 0:
                white_count = self.gameState.getNumBits(white_adj)
            if black_adj > 0:
                black_count = self.gameState.getNumBits(black_adj)
            val_a = -12.5 * (white_count - black_count)

        return val_a

    def getCorners(self, white, black):
        white_count = 0
        black_count = 0

        white_corners = self.gameState.getCorners(white)
        black_corners = self.gameState.getCorners(black)
        if white_corners > 0:
            white_count = self.gameState.getNumBits(white_corners)
        if black_corners > 0:
            black_count = self.gameState.getNumBits(black_corners)

        return 25 * (white_count - black_count)

    def getMobility(self, white, black, empty):
        ratio_m = 0
        white_count = 0
        black_count = 0

        white_valid = self.gameState.getAllValidPlay(white, black, empty)
        black_valid = self.gameState.getAllValidPlay(black, white, empty)
        if white_valid > 0:
            white_count = self.gameState.getNumBits(white_valid)
        if black_valid > 0:
            black_count = self.gameState.getNumBits(black_valid)

        if (white_count > black_count):
            ratio_m = (100.0 * white_count)/(white_count + black_count)
        elif (white_count < black_count):
            ratio_m = (-1 * 100.0 * black_count)/(white_count + black_count)
        return ratio_m
        