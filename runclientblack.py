import client, randomplayer, Chin_player

#replace randomplayer.RandomPlayer with your player
#make sure to specify the color of the player to be 'B'
# blackPlayer = randomplayer.RandomPlayer('B')

blackPlayer = Chin_player.MyPlayer('B')

blackClient = client.Client(blackPlayer)
blackClient.run()
