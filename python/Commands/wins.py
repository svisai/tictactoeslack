from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors

def wins(userkey, teamkey):
    """
    Called on /ttt wins. Prints out the total number of wins for the requesting user. 
    If user has never played a game, returns this info.
    """
    
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()
    
    # Check if player has played game before
    playerid = get_playerid(userkey, teamkey)
    if playerid is None:
        data = {
        "response_type": "ephemeral",
        "text": "You have never played a game of tic tac toe. Start one now with /ttt @opponent!"
        }
    
        resp = Response(json.dumps(data), mimetype='application/json')
        return resp

    
    # Get total wins for current user
    cursor.execute("SELECT total_wins FROM player WHERE player_id = '{0}'".format(playerid))
    num_wins = cursor.fetchone()
    
    # Close connection
    app.mysql.connection.commit()
    cursor.close()
    
    data = {
        "response_type": "in_channel",
        "text": "<@{0}> has {1} tic tac toe wins! You go Glen Coco!".format(username, num_wins[0])
    }
    
    resp = Response(json.dumps(data), mimetype='application/json')
    return resp

