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
                    "text":"To start a game: /ttt start @user\n To display current number of wins and make coworkers jealous: /ttt wins\nTo make a move: /ttt move [position from 0 to 8]\n To end game: /ttt forfeit\n To display board and next player: /ttt status"
                    }
                 ]
        }
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp

def printboard(teamkey, channelkey, userkey):
    """
    Returns formatted current game board and which user has next turn
    """
    gameid = get_gameid(channelkey, teamkey)
    
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()

    # If no current board, return help info
    if gameid is None:
        return help()

    # Query for current players
    cursor.execute("SELECT player_id FROM currentplayer WHERE game_id = {0} AND entry_type = 1".format(gameid))
    player1 = cursor.fetchone()

    cursor.execute("SELECT player_id FROM currentplayer WHERE game_id = {0} AND entry_type = 2".format(gameid))
    player2 = cursor.fetchone()

    cursor.execute("SELECT total_number_moves FROM game WHERE game_id = {0}".format(gameid))
    num_moves = cursor.fetchone()

    if(num_moves[0] % 2 == 0):
        current = player1[0]
    else:
        current = player2[0]

    # Get user name of player who's turn is next
    cursor.execute("SELECT player_name FROM player WHERE player_id = '{0}'".format(current))
    username = cursor.fetchone()

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
    res = "```" + res + "```"

    data = {
        "response_type": "in_channel",
        "text": res,
            "attachments":[
                {
                 "text":"\n<@{0}> is playing next!".format(username[0])
                }
            ]
    }
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp

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
    if(teamid is None):
        return None
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
    if(channelid is None):
        return None
    return channelid[0]

def get_gameid(channelkey, teamkey):
    """
    Returns game_id associated with input of channelkey
    """
    channelid = get_channelid(channelkey, teamkey)
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid))
    gameid = cursor.fetchone()
    app.mysql.connection.commit()
    cursor.close()
    if(gameid is None):
        return None
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
    if(playerid is None):
        return None
    return playerid[0]

def update_game(channelkey, teamkey, new_board):
    """
    Given channelkey and new_board representing updated game board, 
    update total number of moves for game and board game 
    """
    gameid = get_gameid(channelkey, teamkey)
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()	
    cursor.execute("UPDATE game SET total_number_moves=total_number_moves+1 WHERE game_id={0}".format(gameid))
    cursor.execute("UPDATE game SET game_board='{0}' WHERE game_id={1}".format(new_board, gameid))
    app.mysql.connection.commit()
    cursor.close()
    return
