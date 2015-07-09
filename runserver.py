import board, server
 
##Use this code chunk for two automated players
##Remember to run runclientwhite.py and runclientblack.py after runserver.py   
board = board.Board()
white = server.Server(1)
black = server.Server(2)
board.playGame(white, black)

##use this code chunk for white human player and black automated player
##Remember to run runclientblack.py after runserver.py
#board = board.Board()
#white = board
#black = server.Server(2)
#board.playGame(white, black)

##use this code chunk for black human player and white automated player
##Remember to run runclientwhite.py after runserver.py
#board = board.Board()
#white = server.Server(1)
#black = board
#board.playGame(white, black)

