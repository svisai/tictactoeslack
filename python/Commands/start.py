from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from helper import *

def startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, text):
    """
    Called on /ttt start @opponent. This function creates a new game. If requesting player, opponent, channel, or team are not in
    the database, entries are created and initialized for these as well. 
    
    If game exists, will stop the old game and start a new game.
    
    - teamkey: key of requesting team
    - team_domain: domain of requesting team
    - channelkey: key of requesting channel
    - channel_name: name of requesting channel
    - userkey: key of requesting user
    - user_name: name of requesting user
    - text: contains name of opponent user
    
    Returns a message that game has started and who is in new game.
    """
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()
    
    # Get the opponent user name
    user2_name = text[1]
    user2_name = user2_name[1:]

    # Get team_id, create new team if first game in this team
    teamid = get_teamid(teamkey)
    if teamid is None:
        cursor.execute("INSERT INTO team (team_key, team_domain) VALUES ('{0}', '{1}')".format(teamkey, team_domain))
        teamid = get_teamid(teamkey)

     # Get channel_id, create new channel if first game in this channel
    channelid = get_channelid(channelkey, teamkey)
    if channelid is None:
        cursor.execute("INSERT INTO channel (channel_key, team_id, channel_name) VALUES ('{0}', {1}, '{2}')".format(channelkey, teamid, channel_name))
        channelid = get_channelid(channelkey, teamkey)

    # Get player_id for first player, create new player entry if first game with this player
    playerid = get_playerid(userkey, teamkey)
    if playerid is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, team_id, player_name) VALUES ('{0}', {1}, {2},'{3}')".format(userkey, 0, teamid, user_name))
        playerid = get_playerid(userkey, teamkey)

    # Update player key in case player has been stored before as opponent, in which case the player will not have a player_key stored
    cursor.execute("UPDATE player SET player_key='{0}' WHERE player_id='{1}'".format(userkey, playerid))

    # Get player entry for second (opponent) player. If player does not exist, create entry. Player_key will be null as we don't know this player's key until this player makes a request
    cursor.execute("SELECT * FROM player WHERE player_name = '{0}'".format(user2_name))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, team_id, player_name) VALUES ('{0}', {1}, {2},'{3}')".format("", 0, 0, 0, teamid, user2_name))


    channelid = get_channelid(channelkey, teamkey)
    startplayer = get_playerid(userkey, teamkey)

    # Create new game in this channel if one does not exist. If current game exists in this channel, delete this game and create new game with requested player and info.
    gameid = get_gameid(channelkey, teamkey)
    if gameid is not None:
        endgame(channelkey, teamkey)
    cursor.execute("INSERT INTO game (channel_id, start_time, start_player, board_size, game_board, time_limit_move, time_limit_game, result_id, max_players, total_number_moves) VALUES ({0}, NOW(), {1}, {2}, '{3}', {4}, {5}, '{6}', {7}, {8})".format(channelid, startplayer, 3, '---------',5, 120, 0, 2, 0))
    gameid = get_gameid(channelkey, teamkey)

    # Create current player entries for both requesting player and requested opponent
    cursor.execute("INSERT INTO currentplayer (player_id, game_id, entry_type) VALUES ({0}, {1}, {2})".format(startplayer, gameid, 1))
    cursor.execute("SELECT player_id FROM player WHERE player_name = '{0}'".format(user2_name))
    secondplayer = cursor.fetchone()
    cursor.execute("INSERT INTO currentplayer (player_id, game_id, entry_type) VALUES ({0}, {1}, {2})".format(secondplayer[0], gameid, 2))
    
    # Close connection
    app.mysql.connection.commit()
    cursor.close()

    data = {
        "response_type": "in_channel",
        "text":"<@{0}> has started a game of tic tac toe with <@{1}>! Play your first move, <@{2}>.".format(user_name, user2_name, user_name)
    }
    
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp