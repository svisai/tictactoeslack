from flask import *
from helper import *
from move import *
main = Blueprint('main', __name__)

def main(form):
    #temp token will auth later
    #if(request.form['token'] != 'y' or request.form['token'] != 'x'):
    #   return '403 Forbidden'
    values = {}
    teamkey = form['team_id']
    team_domain = form['team_domain']
    channelkey = form['channel_id']
    channel_name = form['channel_name']
    userkey = form['user_id']
    user_name = form['user_name']
    command = form['command']
    text = form['text']
    
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
        return move(teamkey, channelkey, userkey, info[1], user_name)
    elif func == 'forfeit':
        return forfeit(channelkey, teamkey, user_name)
    elif func == 'help':
        return help()
    else:
        return 'Invalid command for tic tac toe. Use /ttt help for info'

