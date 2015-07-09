import client, randomplayer

#replace randomplayer.RandomPlayer with your player
#make sure to specify the color of the player to be 'B'
blackPlayer = randomplayer.RandomPlayer('B')

blackClient = client.Client(blackPlayer)
blackClient.run()
