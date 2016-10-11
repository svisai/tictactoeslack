from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
from helper import *

def forfeit(channelkey, teamkey, username):
    """
    Called on /ttt forfeit to terminate game. Ends game and returns user who ended game if valid
    request, else returns reason for invalid request to user
    """
    channelid = get_channelid(channelkey, teamkey)
    gameid = get_gameid(channelkey, teamkey)
    
    # Check if game exists
    if gameid is None:
        data = {
            "response_type": "ephemeral",
            "text": "No game to forfeit. Start a game now with /ttt start @opponent!"
        }
        return Response(json.dumps(data),  mimetype='application/json')
    
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()
    
    # Ensure requesting player is in a current game
    cursor.execute("SELECT player_id FROM currentplayer WHERE game_id = {0}".format(gameid))
    playerid = cursor.fetchall()

    cursor.execute("SELECT player_id FROM player WHERE player_name = '{0}'".format(username))
    p = cursor.fetchone()
    print p
    print playerid

    valid = 0
    for res in playerid:
        if p[0] == res[0]:
            valid = 1
    if valid == 0:
        data = {
            "response_type": "ephemeral",
            "text": "Must be in current game to forfeit. Start a game now with /ttt start @opponent!"
        }
        return Response(json.dumps(data),  mimetype='application/json')

    # If valid request, end game
    endgame(channelkey, teamkey)

    data = {
        "response_type": "in_channel",
        "text": "<@{0}> has ended their tic tac toe game".format(username)
    }

    resp = Response(json.dumps(data),  mimetype='application/json')
    # Close connection
    app.mysql.connection.commit()
    cursor.close()
    return resp
