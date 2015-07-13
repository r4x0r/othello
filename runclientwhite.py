import client, randomplayer, draft_player

#replace randomPlayer.RandomPlayer with your player
#make sure to specify the color of the player to be 'W'
whitePlayer = draft_player.Player('W')

whiteClient = client.Client(whitePlayer)
whiteClient.run()
