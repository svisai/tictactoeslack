from flask import Flask, Response, render_template, json, request
from flask_mysqldb import MySQL
import os

app = Flask(__name__)


# Configure the MySQL Server
app.mysql = MySQL()
app.config['MYSQL_USER'] = os.environ.get('mysqluser')
app.config['MYSQL_PASSWORD'] = os.environ.get('mysqlpassword')
app.config['MYSQL_DB'] = os.environ.get('mysqldb')
app.config['MYSQL_HOST'] = os.environ.get('mysqlhost')

app.mysql.init_app(app)

@app.route('/ttt', methods=['POST'])
def main():
    #temp token will auth later
    #if(request.form['token'] != 'y' or request.form['token'] != 'x'):
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
    if len(info) < 1:
        return help()
    func = info[0]
    if func == 'start':
        if len(info) < 2:
            return help()
        return startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, command, info)
    elif func == 'status':
        return printboard(teamkey, channelkey)
    elif func == 'move':
        if len(info) < 2:
            return help()
        return move(teamkey, channelkey, userkey, info[1])
    elif func == 'forfeit':
        return forfeit(channelkey, teamkey, user_name)
    elif func == 'help':
        return help()
    else:
        return 'Invalid command for tic tac toe. Use /ttt help for info'
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

def move(teamkey, channelkey, userkey, position):
    cursor = app.mysql.connection.cursor()
    user2_name = request.form['user_name']

    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    cursor.execute("SELECT player_key FROM player WHERE player_name = '{0}' AND team_id = '{1}'".format(user2_name, teamid[0]))

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

    if board[position] != '0':
        return 'The position you requested is occupied'
    if (num_moves % 2 == 0 and playertype != 1) or (num_moves % 2 == 1 and playertype != 2):
        return 'Please wait your turn'

    board = list(board)
    if(num_moves % 2):
        board[position] = 'O'
    else:
        board[position] = 'X'

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

def forfeit(channelkey, teamkey, username):
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

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
