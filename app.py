from flask import Flask, Response, render_template, json, request
from flask_mysqldb import MySQL
import os
from python.Commands.main import main

app = Flask(__name__)


# Configure the MySQL Server
app.mysql = MySQL()
app.config['MYSQL_USER'] = os.environ.get('mysqluser')
app.config['MYSQL_PASSWORD'] = os.environ.get('mysqlpassword')
app.config['MYSQL_DB'] = os.environ.get('mysqldb')
app.config['MYSQL_HOST'] = os.environ.get('mysqlhost')

app.mysql.init_app(app)

#/ttt command route
@app.route('/ttt', methods=['POST'])
def func():
    form = request.form
    return main(form)

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
