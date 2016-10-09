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
    
    cursor = app.mysql.connection.cursor()
    
    exist = cursor.execute("SELECT EXIST(SELECT team_id FROM team WHERE team_key = '{0}')".format(teamkey))
    if exist == 0:
        cursor.execute("INSERT INTO team (team_key, team_domain) VALUES ('{0}', '{1}')".format(teamkey, team_domain))

    teamid = cursor.execute("SELECT team_id FROM team WHERE team_key = '{0}'".format(teamkey))

    exist = cursor.execute("SELECT EXISTS(SELECT * FROM channel WHERE channel_key = '{0}'".format(channelkey))
    if exist == 0:
        cursor.execute("INSERT INTO channel (channel_key, team_id, channel_name) VALUES ('{0}', '{1}', '{2}')".format(channelkey, teamid, channel_name))

    exist = cursor.execute("SELECT EXISTS(SELECT * FROM player WHERE player_key = '{0}'".format(userkey))
    if exist == 0:
        cursor.execute("INSERT INTO player (player_key, total_wins, total_losses, total_ties, team_id, player_name) VALUES ('{0}', {1}, {2}, '{3}', '{4}')".format(userkey, 0, 0, 0, teamid, user_name))
    
    channelid = cursor.execute("SELECT channel_id FROM channel WHERE team_id = '{0}' AND channel_key = '{1}'".format(teamid, channelkey))
    startplayer = cursor.execute("SELECT player_id FROM player WHERE team_id = '{0}' AND player_KEY = '{1}'".format(teamid, userkey))

    exist = cursor.execute("SELECT EXISTS(SELECT * FROM game WHERE channel_id = '{0}' AND start_player = '{1}'".format(channelid, startplayer))
    if exist == 0:
        cursor.execute("INSERT INTO game (channel_id, start_time, end_time, start_player, board_size, game_board, time_limit_move, time_limit_game, result_id, max_players, total_number_moves) VALUES ('{0}', NOW(), '{2}', '{3}', {4}, '{5}', {6}, {7}, {8}, {9})".format(channelid, NULL, startplayer, 3, '000000000',5, 120, 0, 2, 0))

    cursor.close()
    return 'hi'

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
