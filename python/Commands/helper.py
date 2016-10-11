from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors

def help():
    """
    Called on /ttt help. Returns command usage information to user
    """
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
    """
    Returns formatted current game board for printing
    """
    gameid = get_gameid(channelkey)
    
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()

    # If no current board, return help info
    if gameid is None:
        return help()
    
    # Get game board
    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid))
    res = cursor.fetchone()
    b = res[0]

    # Close connection
    app.mysql.connection.commit()
    cursor.close()

    # Format board output
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
    return s

def endgame(channelkey, teamkey):
    """
    Ends current game by deleting game from database. Delete cascades for all current players
    """
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    channelid = get_channelid(channelkey, teamkey)
    cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid))
    return

def get_teamid(teamkey):
    """
    Returns team_id associated with input of teamkey
    """
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    return teamid[0]

def get_channelid(channelkey, teamkey):
    """
    Returns channel_id associated with input of channelkey and teamkey
    """
    teamid = get_teamid(teamkey)
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid, channelkey))
    channelid = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    return channelid[0]

def get_gameid(channelkey):
    """
    Returns game_id associated with input of channelkey
    """
    channelid = get_channellid(channelkey)
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid))
    gameid = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    return gameid[0]

def get_playerid(userkey, teamkey):
    """
    Returns player_id associated with userkey and teamkey
    """
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    teamid = get_teamid(teamkey)
    cursor.execute("SELECT player_id FROM player WHERE team_id = {0} AND player_key = '{1}'".format(teamid, userkey))
    playerid = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    return playerid[0]

def update_game(channelkey, new_board):
    """
    Given channelkey and new_board representing updated game board, 
    update total number of moves for game and board game 
    """
    gameid = get_gameid(channelkey)
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()	
    cursor.execute("UPDATE game SET total_number_moves=total_number_moves+1 WHERE game_id={0}".format(gameid))
    cursor.execute("UPDATE game SET game_board='{0}' WHERE game_id={1}".format(s, gameid))
    app.mysql.connection.commit()
    cursor.close()
    return
