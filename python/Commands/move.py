from flask import *
from helper import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
move = Blueprint('move', __name__)

def move(teamkey, channelkey, userkey, position, user_name):
    """ 
    Called on /ttt move [n], where n is requested position. Returns updated game board if successful request.
    Else, returns note to the user on why invalid request.
    """
    
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()

    # Update playerkey if current player has not made request yet
    teamid = get_teamid(teamkey)
    cursor.execute("SELECT player_key FROM player WHERE player_name = '{0}' AND team_id = '{1}'".format(user_name,teamid))
    
    if cursor.fetchone() is None:
        cursor.execute("UPDATE player SET player_key='{0}' WHERE player_name='{1}'".format(userkey, user_name))
    
    channelid = get_channelid(channelkey, teamkey)
    gameid = get_gameid(channelkey, teamkey)
    playerid = get_playerid(userkey, teamkey)

    # Verify current game exists and current player is in game
    cursor.execute("SELECT player_id FROM currentplayer WHERE player_id = {0}".format(playerid))
    currplayer = cursor.fetchone()

    if gameid is None or currplayer is None:
        data = {
            "response_type": "ephemeral",
            "text": "Must be in current game to play. Start a game now with /ttt start @opponent!"
        }
        return Response(json.dumps(data),  mimetype='application/json')
    
    position = int(position)
    if position > 8:
        data = {
            "response_type": "ephemeral",
            "text": "Requested position is out of bounds"
        }
        return Response(json.dumps(data),  mimetype='application/json')

    # Retrieve total number of moves in game, type of player, and game board
    cursor.execute("SELECT total_number_moves FROM game WHERE game_id = {0}".format(gameid))
    res = cursor.fetchone()
    num_moves = res[0]

    cursor.execute("SELECT entry_type FROM currentplayer WHERE player_id = {0}".format(playerid))
    res = cursor.fetchone()
    playertype = res[0]

    cursor.execute("SELECT game_board FROM game WHERE game_id = {0}".format(gameid))
    res = cursor.fetchone()
    board = res[0]

    # Ensure it is current player's turn and position is available
    if (num_moves % 2 == 0 and playertype != 1) or (num_moves % 2 == 1 and playertype != 2):
        data = {
            "response_type": "ephemeral",
            "text": "Please wait for your turn"
        }
        return Response(json.dumps(data),  mimetype='application/json')
    if board[position] != '-':
        data = {
            "response_type": "ephemeral",
            "text": "Requested position is occupied"
        }
        return Response(json.dumps(data),  mimetype='application/json')

    # Mark board
    board = list(board)
    playernum = 0
    if(playertype == 1):
        board[position] = 'X'
    else:
        board[position] = 'O'

    s = "".join(board)
    # Update board and total number of moves in database
    update_game(channelkey, teamkey, s)

    # Call checkWin on current board to check if move is a winning move, or move resulted in draw
    res = ""
    winner = 0
    cursor.execute("SELECT board_size FROM game WHERE game_id = {0}".format(gameid))
    boardsize = cursor.fetchone()
    winner = checkwin(position, boardsize[0], gameid, playertype)
    
    if(num_moves == 8 and winner == 0):
        endgame(channelkey, teamkey)
        res = "Draw. Game over\n"

    # Update current player's total wins if winning move
    if(winner):
        cursor.execute("UPDATE player SET total_wins=total_wins+1 WHERE player_id={0}".format(currplayer[0]))
        endgame(channelkey, teamkey)
        res =  "<@{0}> won the game! Game over\n".format(user_name)


    # Return win or draw result and updated board
    s = res + str(printboard(teamkey, channelkey))

    app.mysql.connection.commit()
    cursor.close()
    data = {
        "response_type": "in_channel",
        "text":"{0}".format(s)
    }
    resp = Response(json.dumps(data), mimetype='application/json')
    return resp

#increment for player1 (X) and decrement for player 2 (O)
def checkwin(position, boardsize, gameid, playertype):
    """ 
    A function to check if last move was a winning move, and to update stored values for future use by this function.
    For each diagonal, row, and column that position is in, increment total count for that diagonal/row/column if player1,
    decrement if player2. Player1 wins if diagonal/row/column count == 3, player2 wins if count == -3. 
    
    Thus checking for winner operates in O(1).
    
    eg: If position is 0 in board, and player is player1, increment diag0, row0, and column0 in database.
    If position is 1 in board, and player is player2, decrement row0 and column1 in database.
    
        - gameid: id of current game
        - boardsize: size of board
        - position: the last position marked in move request
        - player: is player player1 ('X') or player2 ('O')
        
    returns 1 if player1 wins, 2 if player2 wins, and 0 if draw or no win
    """
    # Get the global application object
    app = current_app._get_current_object()
    # Get the mysql object from app and create a connection
    cursor = app.mysql.connection.cursor()
    
    # Calculate column and row that position is in
    column = position % boardsize
    row = position / boardsize
    
    win = 0
    
    # Update diagonal value if position is in diagonal
    if(column == row):
        if(playertype == 1):
            cursor.execute("UPDATE game SET diag0=diag0+1 WHERE game_id={0}".format(gameid))
        else:
            cursor.execute("UPDATE game SET diag0=diag0-1 WHERE game_id={0}".format(gameid))

        # Check for winner
        cursor.execute("SELECT diag0 FROM game WHERE game_id={0}".format(gameid))
        res = cursor.fetchone()
        if(playertype == 1 and res[0] == boardsize):
            win = 1
        elif(playertype == 2 and res[0] == boardsize * -1):
            win = 2

    # Update anti-diagonal value if position is in anti-diagonal
    elif(column == boardsize - row - 1):
        if(playertype == 1):
            cursor.execute("UPDATE game SET diag1=diag1+1 WHERE game_id={0}".format(gameid))
        else:
            cursor.execute("UPDATE game SET diag1=diag1-1 WHERE game_id={0}".format(gameid))
        
        # Check for winner
        cursor.execute("SELECT diag1 FROM game WHERE game_id={0}".format(gameid))
        res = cursor.fetchone()
        if(playertype == 1 and res[0] == boardsize):
            win = 1
        elif(playertype == 2 and res[0] == boardsize * -1):
            win = 2

    # Update row and column values that position is in
    if(playertype == 1):
        cursor.execute("UPDATE game SET row{0}=row{1}+1 WHERE game_id={2}".format(row, row, gameid))
        cursor.execute("UPDATE game SET column{0}=column{1}+1 WHERE game_id={2}".format(column, column, gameid))
    else:
        cursor.execute("UPDATE game SET row{0}=row{1}-1 WHERE game_id={2}".format(row, row, gameid))
        cursor.execute("UPDATE game SET column{0}=column{1}-1 WHERE game_id={2}".format(column, column, gameid))
    
    # Check for a win in row or column
    cursor.execute("SELECT row{0} FROM game WHERE game_id={1}".format(row, gameid))
    res = cursor.fetchone()
    if(playertype == 1 and res[0] == boardsize):
        win = 1
    elif(playertype == 2 and res[0] == boardsize * -1):
        win = 2

    cursor.execute("SELECT column{0} FROM game WHERE game_id={1}".format(column, gameid))
    res = cursor.fetchone()
    if(playertype == 1 and res[0] == boardsize):
        win = 1
    elif(playertype == 2 and res[0] == boardsize * -1):
        win = 2

    # Close connection
    app.mysql.connection.commit()
    cursor.close()
    return win
