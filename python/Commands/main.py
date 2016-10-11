from flask import *
from helper import *
from start import *
from move import *
from wins import *
from forfeit import *
main = Blueprint('main', __name__)

def main(form):
    """
    Parses incoming request of form /ttt func [args] and calls appropriate function. If invalid request format,
    returns help information to the user
    """
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
    # No function specified
    if len(info) < 1:
        return help()
    func = info[0]
    # Start a new game. Ensure competing user is specfied, eg /ttt user @opponent
    if func == 'start':
        if len(info) < 2:
            return help()
        return startgame(teamkey, team_domain, channelkey, channel_name, userkey, user_name, info)
    # Print game board
    elif func == 'status':
        return printboard(teamkey, channelkey)
    # Make a game move. Ensure position is specified, eg /ttt move [position]
    elif func == 'move':
        if len(info) < 2:
            return help()
        return move(teamkey, channelkey, userkey, info[1], user_name)
    # Forfeit current game
    elif func == 'forfeit':
        return forfeit(channelkey, teamkey, user_name)
    # Print total number of wins for this user
    elif func == 'wins':
        return wins(user_name, userkey, teamkey)
    # Return help info to user
    elif func == 'help':
        return help()
    else:
        data = {
            "response_type": "ephemeral",
            "text": "Invalid command for /ttt. Use /ttt help for more info"
        }
        
        resp = Response(json.dumps(data), mimetype='application/json')
        return resp

