drop table if exists team;
create table team (
    team_id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(team_id)
    team_key VARCHAR(20) NOT NULL,
    team_domain VARCHAR(50)
);

drop table if exists channel;
create table channel (
    channel_id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(channel_id),
    channel_key VARCHAR(20) NOT NULL,
    channel_name VARCHAR(20),
    team_id INTEGER,
    FOREIGN KEY (team_id)
        REFERENCES team(team_id)
        ON DELETE CASCADE
);

drop table if exists player;
create table player (
    player_id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(player_id),
    player_key VARCHAR(20),
    total_wins INTEGER,
    total_losses INTEGER,
    total_ties INTEGER
    team_id INTEGER,
    player_name VARCHAR(20),
    FOREIGN KEY (team_id)
    REFERENCES team(team_id)
        ON DELETE CASCADE,
);


drop table if exists game;
create table game (
    game_id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(game_id),
    channel_id INTEGER,
    FOREIGN KEY (channel_id)
        REFERENCES channel(channel_id)
        ON DELETE CASCADE,
    start_time DATETIME,
    end_time DATETIME,
    start_player INTEGER,
    FOREIGN KEY (start_player)
        REFERENCES player(player_id)
        ON DELETE CASCADE,
    board_size INT,
    game_board varchar(9),
    time_limit_move INT,
    time_limit_game INT,
    result_id VARCHAR(20),
    max_players INT,
    total_number_moves INT,
    column0 INTEGER,
    column1 INTEGER,
    column2 INTEGER,
    row0 INTEGER,
    row1 INTEGER,
    row2 INTEGER,
    diag0 INTEGER,
    diag1 INTEGER
);

drop table if exists currentplayer;
create table currentplayer (
    currentplayer_id INTEGER NOT NULL AUTO_INCREMENT,
    PRIMARY KEY(currentplayer_id),
    player_id  INTEGER,
    FOREIGN KEY (player_id)
        REFERENCES player(player_id)
        ON DELETE CASCADE,
    game_id INTEGER,
    FOREIGN KEY (game_id)
    REFERENCES game(game_id)
    ON DELETE CASCADE,
    entry_type INTEGER
);