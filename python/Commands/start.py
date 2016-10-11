from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

def startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, command, text):
    app = current_app._get_current_object()
    user2_name = text[1]
    user2_name = user2_name[1:]
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO team (team_key, team_domain) VALUES ('{0}', '{1}')".format(teamkey, team_domain))
    
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()

    cursor.execute("SELECT * FROM channel WHERE channel_key = '{0}'".format(channelkey))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO channel (channel_key, team_id, channel_name) VALUES ('{0}', {1}, '{2}')".format(channelkey, teamid[0], channel_name))

    cursor.execute("SELECT * FROM player WHERE player_name = '{0}'".format(user_name))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, total_losses, total_ties, team_id, player_name) VALUES ('{0}', {1}, {2}, {3}, {4}, '{5}')".format(userkey, 0, 0, 0, teamid[0], user_name))
    cursor.execute("UPDATE player SET player_key='{0}' WHERE player_name='{1}'".format(userkey, user_name))
    
    cursor.execute("SELECT * FROM player WHERE player_name = '{0}'".format(user2_name))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, total_losses, total_ties, team_id, player_name) VALUES ('{0}', {1}, {2}, {3}, {4}, '{5}')".format("", 0, 0, 0, teamid[0], user2_name))
    
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("SELECT player_id FROM player WHERE team_id = {0} AND player_key = '{1}'".format(teamid[0], userkey))
    startplayer = cursor.fetchone()
    
    cursor.execute("SELECT * FROM game WHERE channel_id = {0}".format(channelid[0]))
    if cursor.fetchone() is not None:
        cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid[0]))
    cursor.execute("INSERT INTO game (channel_id, start_time, start_player, board_size, game_board, time_limit_move, time_limit_game, result_id, max_players, total_number_moves) VALUES ({0}, NOW(), {1}, {2}, '{3}', {4}, {5}, '{6}', {7}, {8})".format(channelid[0], startplayer[0], 3, '---------',5, 120, 0, 2, 0))

    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    
    cursor.execute("INSERT INTO currentplayer (player_id, game_id, entry_type) VALUES ({0}, {1}, {2})".format(startplayer[0], gameid[0], 1))
    
    cursor.execute("SELECT player_id FROM player WHERE player_name = '{0}'".format(user2_name))
    secondplayer = cursor.fetchone()
    cursor.execute("INSERT INTO currentplayer (player_id, game_id, entry_type) VALUES ({0}, {1}, {2})".format(secondplayer[0], gameid[0], 2))
    
    
    app.mysql.connection.commit()
    cursor.close()
    data = {
        "response_type": "in_channel",
        "text":"<@{0}> has started a game of tic tac toe with <@{1}>! Play your first move, <@{2}>.".format(user_name, user2_name, user_name)
    }
    
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp