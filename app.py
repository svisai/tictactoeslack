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
    if(request.form['token'] != 'O8s7mBAq8Q3HvFj9lghw6RVI'):
        return 'Forbidden'
    
    values = {}
    teamkey = request.form['team_id']
    team_domain = request.form['team_domain']
    channelkey = request.form['channel_id']
    channel_name = request.form['channel_name']
    userkey = request.form['user_id']
    user_name = request.form['user_name']
    command = request.form['command']
    text = request.form['text']
    user2_name = request.form['text']
    user2_name = user2_name[1:]
    cursor = app.mysql.connection.cursor()

    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO team (team_key, team_domain) VALUES ('{0}', '{1}')".format(teamkey, team_domain))
        app.mysql.connection.commit()

    cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))
    teamid = cursor.fetchone()
    print(teamid)

    cursor.execute("SELECT * FROM channel WHERE channel_key = '{0}'".format(channelkey))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO channel (channel_key, team_id, channel_name) VALUES ('{0}', {1}, '{2}')".format(channelkey, teamid[0], channel_name))
        app.mysql.connection.commit()

    cursor.execute("SELECT * FROM player WHERE player_key = '{0}'".format(userkey))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, total_losses, total_ties, team_id, player_name) VALUES ('{0}', {1}, {2}, {3}, {4}, '{5}')".format(userkey, 0, 0, 0, teamid[0], user_name))
        app.mysql.connection.commit()

    cursor.execute("SELECT * FROM player WHERE player_name = '{0}'".format(user2_name))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO player (player_key, total_wins, total_losses, total_ties, team_id, player_name) VALUES ('{0}', {1}, {2}, {3}, {4}, '{5}')".format("", 0, 0, 0, teamid[0], user2_name))
        app.mysql.connection.commit()


    cursor.execute("SELECT channel_id FROM channel WHERE team_id = {0} AND channel_key = '{1}'".format(teamid[0], channelkey))
    channelid = cursor.fetchone()
    cursor.execute("SELECT player_id FROM player WHERE team_id = {0} AND player_key = '{1}'".format(teamid[0], userkey))
    startplayer = cursor.fetchone()

    cursor.execute("SELECT * FROM game WHERE channel_id = {0}".format(channelid[0]))
    if cursor.fetchone() is not None:
        cursor.execute("DELETE FROM game WHERE channel_id = {0}".format(channelid[0]))
    cursor.execute("INSERT INTO game (channel_id, start_time, start_player, board_size, game_board, time_limit_move, time_limit_game, result_id, max_players, total_number_moves) VALUES ({0}, NOW(), {1}, {2}, '{3}', {4}, {5}, '{6}', {7}, {8})".format(channelid[0], startplayer[0], 3, '000000000',5, 120, 0, 2, 0))
    app.mysql.connection.commit()

    cursor.execute("SELECT game_id FROM game WHERE channel_id = {0}".format(channelid[0]))
    gameid = cursor.fetchone()
    secondplayer = cursor.fetchone()
    cursor.execute("INSERT INTO currentplayer (player_id, game_id) VALUES ({0}, {1})".format(startplayer[0], gameid[0]))
    app.mysql.connection.commit()
    cursor.execute("SELECT player_id FROM player WHERE player_name = '{0}'".format(user2_name))
    secondplayer = cursor.fetchone()
    cursor.execute("INSERT INTO currentplayer (player_id, game_id) VALUES ({0}, {1})".format(secondplayer[0], gameid[0]))
    app.mysql.connection.commit()


    cursor.close()
    return "Hi @{0}! You've started a game of tic tac toe with @{1}! Play your first move.".format(user_name, user2_name)

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
