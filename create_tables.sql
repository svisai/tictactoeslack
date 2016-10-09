drop table if exists team;
create table team (
    team_id VARCHAR(6) NOT NULL,
    PRIMARY KEY(team_id)
);

drop table if exists channel;
create table channel (
channel_id VARCHAR(20) NOT NULL,
PRIMARY KEY(channel_id),
team_id VARCHAR(6),
FOREIGN KEY (team_id)
REFERENCES team(team_id)
ON DELETE CASCADE
);

drop table if exists player;
create table player (
    player_id VARCHAR(20),
    PRIMARY KEY(player_id),
    total_wins INT,
    total_losses INT,
    total_ties INT
);


drop table if exists game;
create table game (
game_id INTEGER NOT NULL AUTO_INCREMENT,
PRIMARY KEY(game_id),
channel_id VARCHAR(20),
FOREIGN KEY (channel_id)
REFERENCES channel(channel_id)
ON DELETE CASCADE,
start_time DATETIME,
end_time DATETIME,
start_player VARCHAR(20),
FOREIGN KEY (start_player)
REFERENCES player(player_id)
ON DELETE CASCADE,
board_size INT,
game_board varchar(9),
time_limit_move INT,
time_limit_game INT,
result_id VARCHAR(20),
max_players INT,
total_number_moves INT
);