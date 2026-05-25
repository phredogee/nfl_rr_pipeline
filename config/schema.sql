-- NFL RR Pipeline Database Schema
-- Tables: schedules, rosters, weekly_stats
-- Run this once to initialize the database structure

-- Drop tables if they exist (useful for clean resets during dev)
DROP TABLE IF EXISTS weekly_stats;
DROP TABLE IF EXISTS rosters;
DROP TABLE IF EXISTS schedules;

-- Schedule table: one row per game
CREATE TABLE schedules (
    game_id         VARCHAR(20) PRIMARY KEY,
    season          INTEGER NOT NULL,
    game_type       VARCHAR(10),
    week            INTEGER,
    gameday         DATE,
    weekday         VARCHAR(10),
    gametime        VARCHAR(10),
    away_team       VARCHAR(10),
    home_team       VARCHAR(10),
    away_score      INTEGER,
    home_score      INTEGER,
    stadium         VARCHAR(100),
    roof            VARCHAR(20),
    surface         VARCHAR(20),
    temp            FLOAT,
    wind            FLOAT
);

-- Roster table: one row per player per season
CREATE TABLE rosters (
    player_id               VARCHAR(20),
    season                  INTEGER NOT NULL,
    team                    VARCHAR(10),
    position                VARCHAR(10),
    depth_chart_position    VARCHAR(10),
    jersey_number           INTEGER,
    full_name               VARCHAR(100),
    birth_date              DATE,
    height                  VARCHAR(10),
    weight                  INTEGER,
    college                 VARCHAR(100),
    years_exp               INTEGER,
    status                  VARCHAR(20),
    PRIMARY KEY (player_id, season, team)
);

-- Weekly stats table: one row per player per week
-- Columns marked [LIVE API] will be NULL until live API integration
CREATE TABLE weekly_stats (
    player_id                   VARCHAR(20),
    player_name                 VARCHAR(100),
    season                      INTEGER NOT NULL,
    week                        INTEGER NOT NULL,
    season_type                 VARCHAR(10),
    team                        VARCHAR(10),
    opponent                    VARCHAR(10),
    position                    VARCHAR(10),

    -- Passing
    completions                 INTEGER,
    attempts                    INTEGER,
    passing_yards               FLOAT,
    passing_tds                 INTEGER,
    interceptions               INTEGER,
    sacks                       FLOAT,
    sack_yards                  FLOAT,
    sack_fumbles_lost           INTEGER,
    passing_2pt_conversions     INTEGER,
    passing_air_yards           FLOAT,
    passing_yards_after_catch   FLOAT,
    passing_first_downs         INTEGER,

    -- Rushing
    carries                     INTEGER,
    rushing_yards               FLOAT,
    rushing_tds                 INTEGER,
    rushing_fumbles             INTEGER,
    rushing_fumbles_lost        INTEGER,
    rushing_2pt_conversions     INTEGER,
    rushing_first_downs         INTEGER,

    -- Receiving
    targets                     INTEGER,
    receptions                  INTEGER,
    receiving_yards             FLOAT,
    receiving_tds               INTEGER,
    receiving_fumbles           INTEGER,
    receiving_fumbles_lost      INTEGER,
    receiving_2pt_conversions   INTEGER,
    receiving_air_yards         FLOAT,
    receiving_yards_after_catch FLOAT,
    receiving_first_downs       INTEGER,

    -- Misc offense
    special_teams_tds           INTEGER,

    -- Kicking [LIVE API]
    pat_made                    INTEGER,
    pat_missed                  INTEGER,
    fg_made_0_39                INTEGER,
    fg_made_40_49               INTEGER,
    fg_made_50_plus             INTEGER,
    fg_missed_0_39              INTEGER,
    fg_missed_40_49             INTEGER,
    fg_missed_50_plus           INTEGER,

    -- DST [LIVE API]
    dst_sacks                   INTEGER,
    dst_interceptions           INTEGER,
    dst_fumbles_recovered       INTEGER,
    dst_touchdowns              INTEGER,
    dst_safeties                INTEGER,
    dst_blocked_kicks           INTEGER,
    dst_return_tds              INTEGER,
    dst_three_and_outs          INTEGER,
    dst_fourth_down_stops       INTEGER,
    dst_points_allowed          INTEGER,
    dst_yards_allowed           INTEGER,

    -- Pre-calculated (keep for reference/fallback)
    fantasy_points              FLOAT,
    fantasy_points_ppr          FLOAT,

    PRIMARY KEY (player_id, season, week, team)
);
