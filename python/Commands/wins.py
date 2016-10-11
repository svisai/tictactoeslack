from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors

def wins(username, teamkey):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT total_wins FROM player WHERE team_id = {0} AND player_name = '{1}'".format(teamid[0], username))
    num_wins = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    data = {
        "response_type": "in_channel",
        "text": "<@{0}> has {1} tic tac toe wins! You go Glen Coco!".format(username, num_wins[0])
    }
    resp = Response(json.dumps(data), mimetype='application/json')
    return resp

