from flask import Flask, render_template, json, request
from flask_mysqldb import MySQL
import os

app = Flask(__name__)


# Configure the MySQL Server
app.mysql = MySQL()
app.config['MYSQL_USER'] = 'b52ea2241ff58f'
app.config['MYSQL_PASSWORD'] = 'bb8d37ad'
app.config['MYSQL_DB'] = 'heroku_a09bdcabd272d7a'
app.config['MYSQL_HOST'] = 'us-cdbr-iron-east-04.cleardb.net'

app.mysql.init_app(app)

@app.route('/ttt', methods=['POST'])
def main():
    #if(request.form['token'] != 'O8s7mBAq8Q3HvFj9lghw6RVI' or request.form['token'] != 'osSz1E86vqGCOJRp8f9nh1cu'):
    #   return '403 Forbidden'
    
    values = {}
    teamkey = request.form['team_id']
    team_domain = request.form['team_domain']
    channelkey = request.form['channel_id']
    channel_name = request.form['channel_name']
    userkey = request.form['user_id']
    user_name = request.form['user_name']
    command = request.form['command']
    text = request.form['text']
    
    info = text.split()
    func = info[0]
    if func == 'start':
        return startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, command, info)
    elif func == 'status':
        return printboard(teamkey, channelkey)
    elif func == 'move':
        return move(teamkey, channelkey, userkey, info[1])
    elif func == 'help':
        return 'To start a game: /ttt start @user\n To make a move: /ttt move [position from 0 to 8]\n To end game: /ttt forfeit\n To display board: /ttt status'
    else:
        return 'Invalid command for tic tac toe. Use /ttt help for info'

def move(teamkey, channelkey, userkey, position):
    cursor = app.mysql.connection.cursor()
    user2_name = request.form['user_name']
    position = int(position)
    if position > 8:
        return 'Position out of bounds'
    cursor.execute("SELECT * FROM player WHERE player_name = '{0}'".format(user2_name))

    if cursor.fetchone() is not None:
        cursor.execute("UPDATE player SET player_key='{0}' WHERE player_name={1}".format(s, request.form['user_id']))
    else:
        return 'Join a game to play'

    #Verify existing game including requesting player
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
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

    cursor.execute("SELECT total_number_moves FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    num_moves = res[0]
    cursor.execute("SELECT entry_type FROM currentplayer WHERE player_id = {0}".format(playerid[0]))
    res = cursor.fetchone()
    playertype = res[0]
    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    board = res[0]

    if board[position] != '0':
        return 'The position you requested is occupied'
    if (num_moves % 2 == 0 and playertype != 1) or (num_moves % 2 == 1 and playertype != 2):
        return 'Please wait your turn'

    board = list(board)
    if(num_moves % 2):
        board[position] = 'X'
    else:
        board[position] = 'O'

    s = "".join(board)
    cursor.execute("UPDATE game SET total_number_moves=total_number_moves+1 WHERE game_id={0}".format(gameid[0]))
    cursor.execute("UPDATE game SET game_board='{0}' WHERE game_id={1}".format(s, gameid[0]))
    app.mysql.connection.commit()
    cursor.close()
    return printboard(teamkey, channelkey)

def printboard(teamkey, channelkey):
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid[0]))
    res = cursor.fetchone()
    b = res[0]
    app.mysql.connection.commit()
    cursor.close()
    b = list(b)
    res = ""
    res += '|'
    for i in range(0,3):
        res += b[i] + '|' + " "
    res += '\n'
    res +=  '|'
    for i in range(3,6):
        res +=  b[i] + '|' + " "
    res +=  '\n'
    res +=  '|'
    for i in range(6,9):
        res +=  b[i] + '|' + " "
    res +=  '\n'
    return res

def startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, command, text):
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
    return "Hi @{0}! You've started a game of tic tac toe with @{1}! Play your first move.".format(user_name, user2_name)

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
