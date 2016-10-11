from flask import *
import helper
from flask_mysqldb import MySQL
import os
from python.Commands.main import main
move = Blueprint('move', __name__)

def move(teamkey, channelkey, userkey, position, user2_name):
    cursor = app.mysql.connection.cursor()
    
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT player_key FROM player WHERE player_name = '{0}' AND team_id = '{1}'".format(user2_name,teamid[0]))
    
    if cursor.fetchone() is None:
        cursor.execute("UPDATE player SET player_key='{0}' WHERE player_name='{1}'".format(userkey, user2_name))
    
    #Verify existing game including requesting player
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    cursor.execute("SELECT player_id FROM player WHERE team_id = {0} AND player_key = '{1}'".format(teamid[0], userkey))
    playerid = cursor.fetchone()
    cursor.execute("SELECT player_id FROM currentplayer WHERE player_id = {0}".format(playerid[0]))
    currplayer = cursor.fetchone()
    if gameid is None or currplayer is None:
        return 'Join a game to play'
    
    position = int(position)
    if position > 8:
        return 'Position out of bounds'
    
    cursor.execute("SELECT total_number_moves FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    num_moves = res[0]
    cursor.execute("SELECT entry_type FROM currentplayer WHERE player_id = {0}".format(playerid[0]))
    res = cursor.fetchone()
    playertype = res[0]
    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    board = res[0]

    if (num_moves % 2 == 0 and playertype != 1) or (num_moves % 2 == 1 and playertype != 2):
        return 'Please wait your turn'
    if board[position] != '0':
        return 'The position you requested is occupied'

    board = list(board)
    playernum = 0
    if(num_moves % 2 == 0):
        board[position] = 'X'
        playernum = 1
    else:
        board[position] = 'O'
        playernum = 2
    
    cursor.execute("SELECT board_size FROM game WHERE game_id = {0}".format(gameid[0]))
    boardsize = cursor.fetchone()
    boardsize = boardsize[0]

    s = "".join(board)
    cursor.execute("UPDATE game SET total_number_moves=total_number_moves+1 WHERE game_id={0}".format(gameid[0]))
    cursor.execute("UPDATE game SET game_board='{0}' WHERE game_id={1}".format(s, gameid[0]))
    
    res = ""
    winner = 0
    winner = checkwin(position, boardsize, gameid, num_moves)
    
    if(num_moves == 8 and winner == 0):
        endgame(channelkey, teamkey)
        res = 'There has been a tie. Game ended'
    
    if(winner):
        cursor.execute("UPDATE player SET total_wins=total_wins+1 WHERE player_id={0}".format(currplayer[0]))
        endgame(channelkey, teamkey)
        res =  "<@{0}> won the game! Game over".format(user2_name)
    if(res == ""):
        return printboard(teamkey, channelkey)
    
    app.mysql.connection.commit()
    cursor.close()

    return res
