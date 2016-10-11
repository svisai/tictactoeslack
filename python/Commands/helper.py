from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

def help():
    data = {
        "response_type": "ephemeral",
            "text": "How to use /ttt",
                "attachments":[
                    {
                    "text":"To start a game: /ttt start @user\n To display current number of wins and make coworkers jealous: /ttt wins\nTo make a move: /ttt move [position from 0 to 8]\n To end game: /ttt forfeit\n To display board: /ttt status"
                    }
                 ]
        }
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp

def printboard(teamkey, channelkey):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    if gameid is None:
        return help()
    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    b = res[0]
    app.mysql.connection.commit()
    cursor.close()
    b = list(b)
    res = ""
    res += '| '
    for i in range(0,3):
        res += b[i] + " " + '| '
    res += '\n'
    res += '|---+---+---|'
    res += '\n'
    res +=  '| '
    for i in range(3,6):
        res +=  b[i] + ' | '
    res += '\n'
    res += '|---+---+---|'
    res += '\n'
    res +=  '| '
    for i in range(6,9):
        res +=  b[i] + ' | '
    res += '\n'
    res += '|---+---+---|'
    res += '\n'
    s = "```" + res + "```"
    data = {
        "response_type": "in_channel",
        "text": s
    }
    resp = Response(json.dumps(data), mimetype='application/json')
    return resp

def endgame(channelkey, teamkey):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid[0]))
    return 'Game ended'
