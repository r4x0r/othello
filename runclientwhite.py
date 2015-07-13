
import client, randomplayer, playerv2, playerv3



#replace randomPlayer.RandomPlayer with your player
#make sure to specify the color of the player to be 'W'
whitePlayer = playerv3.Player('W')

whiteClient = client.Client(whitePlayer)
whiteClient.run()
