from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors

def forfeit(channelkey, teamkey, username):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    
    cursor.execute("SELECT * FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    if gameid is None:
        return 'No current game to forfeit'
    
    cursor.execute("SELECT player_id FROM currentplayer WHERE game_id = {0}".format(gameid[0]))
    playerid = cursor.fetchall()
    valid = 0
    for res in playerid:
        cursor.execute("SELECT player_id FROM player WHERE player_name = '{0}'".format(username))
        p = cursor.fetchone()
        if p == res:
            valid = 1
    if valid == 0:
        return 'Must be in a current game to forfeit'
    
    cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid[0]))
    data = {
        "response_type": "in_channel",
        "text": "<@{0}> has ended their tic tac toe game".format(username)
    }
    resp = Response(json.dumps(data),  mimetype='application/json')
    app.mysql.connection.commit()
    cursor.close()
    return resp
