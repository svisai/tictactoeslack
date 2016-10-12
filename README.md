
# Tic Tac Toe for Slack
A custom slash command to play tic tac toe within a Slack channel

## To use
Create a custom slash command for your Slack team. Name the comand /ttt. Use the URL `http://slackcommandttt.herokuapp.com/ttt`. 
Will need to modify code to use generated token.

## Commands
- `/tttt start @username` Starts a new game with opponent @username
- `/tttt move [n]` Makes a move on game board in position n
- `/tttt wins` Displays current total number of wins for user
- `/tttt forfeit` End current game
- `/tttt status` Displays current board
- `/tttt help` How to use command

### Install
```shell
$ pip install Flask
```

### Built With
Flask, Python, MySQL
Hosted on Heroku