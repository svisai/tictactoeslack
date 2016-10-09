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
    team_id = request.form['team_id']
    team_domain = request.form['team_domain']
    channel_id = request.form['channel_id']
    channel_name = request.form['channel_name']
    user_id = request.form['user_id']
    user_name = request.form['user_name']
    command = request.form['command']
    text = request.form['text']
    
    cursor = app.mysql.connection.cursor()
    cursor.execute("INSERT INTO team (team_id) VALUES (%s)", team_id)
    return 'Welcome to your tic tac toe game! Make your first move'

def load():
    cursor = app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM hi")
    
    data = cursor.fetchall()
    str = data[0]
    cursor.close()

    return 'works!'


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
