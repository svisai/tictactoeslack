from flask import Flask, Response, render_template, json, request
from flask_mysqldb import MySQL
import os
from python.Commands.main import main

def help():
    data = {
        "response_type": "ephemeral",
            "text": "How to use /ttt",
                "attachments":[
                    {
                    "text":"To start a game: /ttt start @user\n To make a move: /ttt move [position from 0 to 8]\n To end game: /ttt forfeit\n To display board: /ttt status"
                    }
                 ]
        }
    resp = Response(json.dumps(data),  mimetype='application/json')
    return resp

#increment for player1 (X) and decrement for player 2 (O)
def checkwin(position, boardsize, gameid, num_moves):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    column = position % boardsize
    row = position / boardsize
    
    win = 0
    if(column == row):
        if(num_moves % 2 == 0):
            cursor.execute("UPDATE game SET diag0=diag0+1 WHERE game_id={0}".format(gameid[0]))
        else:
            cursor.execute("UPDATE game SET diag0=diag0-1 WHERE game_id={0}".format(gameid[0]))
        cursor.execute("SELECT diag0 FROM game WHERE game_id={0}".format(gameid[0]))
        res = cursor.fetchone()
        if(num_moves % 2 == 0 and res[0] == boardsize):
            win = 1
        elif(num_moves % 2 == 1 and res[0] == boardsize * -1):
            win = 2


    elif(column == boardsize - row - 1):
        if(num_moves % 2 == 0):
            cursor.execute("UPDATE game SET diag1=diag1+1 WHERE game_id={0}".format(gameid[0]))
        else:
            cursor.execute("UPDATE game SET diag1=diag1-1 WHERE game_id={0}".format(gameid[0]))
        cursor.execute("SELECT diag1 FROM game WHERE game_id={0}".format(gameid[0]))
        res = cursor.fetchone()
        if(num_moves % 2 == 0 and res[0] == boardsize):
            win = 1
        elif(num_moves % 2 == 1 and res[0] == boardsize * -1):
            win = 2
    
    if(num_moves % 2 == 0):
        cursor.execute("UPDATE game SET row{0}=row{1}+1 WHERE game_id={2}".format(row, row, gameid[0]))
        cursor.execute("UPDATE game SET column{0}=column{1}+1 WHERE game_id={2}".format(column, column, gameid[0]))
    else:
        cursor.execute("UPDATE game SET row{0}=row{1}-1 WHERE game_id={2}".format(row, row, gameid[0]))
        cursor.execute("UPDATE game SET column{0}=column{1}-1 WHERE game_id={2}".format(column, column, gameid[0]))
    
    #check win
    cursor.execute("SELECT row{0} FROM game WHERE game_id={1}".format(row, gameid[0]))
    res = cursor.fetchone()
    if(num_moves % 2 == 0 and res[0] == boardsize):
        win = 1
    elif(num_moves % 2 == 1 and res[0] == boardsize * -1):
        win = 2
    cursor.execute("SELECT column{0} FROM game WHERE game_id={1}".format(column, gameid[0]))
    res = cursor.fetchone()
    if(num_moves % 2 == 0 and res[0] == boardsize):
        win = 1
    elif(num_moves % 2 == 1 and res[0] == boardsize * -1):
        win = 2
    app.mysql.connection.commit()
    cursor.close()
    return win

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
    res += '\n'
    res += '-------------'
    res += '\n'
    res += '|'
    for i in range(0,3):
        res += b[i] + '|' + " "
    res += '\n'
    res += '-------------'
    res += '\n'
    res +=  '|'
    for i in range(3,6):
        res +=  b[i] + '|' + " "
    res += '\n'
    res += '-------------'
    res += '\n'
    res +=  '|'
    for i in range(6,9):
        res +=  b[i] + '|' + " "
    res += '\n'
    res += '-------------'
    res += '\n'
    return res

def endgame(channelkey, teamkey):
    app = current_app._get_current_object()
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid[0]))
    return 'Game ended'

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
    cursor.execute("INSERT INTO game (channel_id, start_time, start_player, board_size, game_board, time_limit_move, time_limit_game, result_id, max_players, total_number_moves) VALUES ({0}, NOW(), {1}, {2}, '{3}', {4}, {5}, '{6}', {7}, {8})".format(channelid[0], startplayer[0], 3, '000000000',5, 120, 0, 2, 0))

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
