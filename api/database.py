import sqlite3
import pandas as pd

DATABASE_FILE = 'fpl.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT UNIQUE NOT NULL,
            fpl_team_code INTEGER
        )
    ''')

    # Create players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            position TEXT NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (team_id)
        )
    ''')

    # Create fbref player stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats_fbref (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            nation TEXT,
            pos TEXT,
            age INTEGER,
            born INTEGER,
            playing_time_mp INTEGER,
            playing_time_starts INTEGER,
            playing_time_min INTEGER,
            playing_time_90s REAL,
            performance_gls INTEGER,
            performance_ast INTEGER,
            performance_g_a INTEGER,
            performance_g_pk INTEGER,
            performance_pk INTEGER,
            performance_pkatt INTEGER,
            performance_crdy INTEGER,
            performance_crdr INTEGER,
            expected_xg REAL,
            expected_npxg REAL,
            expected_xag REAL,
            expected_npxg_xag REAL,
            progression_prgc REAL,
            progression_prgp REAL,
            progression_prgr REAL,
            per_90_minutes_gls REAL,
            per_90_minutes_ast REAL,
            per_90_minutes_g_a REAL,
            per_90_minutes_g_pk REAL,
            per_90_minutes_g_a_pk REAL,
            per_90_minutes_xg REAL,
            per_90_minutes_xag REAL,
            per_90_minutes_xg_xag REAL,
            per_90_minutes_npxg REAL,
            per_90_minutes_npxg_xag REAL,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
    ''')

    conn.commit()
    conn.close()

def populate_teams_and_players(players_data, teams_data):
    """
    Populates the teams and players tables from the FPL player data, mapping to the new schema.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Teams Population ---
    teams_df = pd.DataFrame(teams_data)
    teams_df = teams_df[['id', 'name', 'code']]
    teams_df = teams_df.rename(columns={'id': 'team_id', 'name': 'team_name', 'code': 'fpl_team_code'})
    teams_to_insert = teams_df.to_dict(orient='records')
    cursor.executemany(
        "INSERT OR IGNORE INTO teams (team_id, team_name, fpl_team_code) VALUES (:team_id, :team_name, :fpl_team_code)",
        teams_to_insert
    )

    # --- Players Population ---
    players_df = pd.DataFrame(players_data)
    # Create full_name
    players_df['full_name'] = players_df['first_name'] + ' ' + players_df['second_name']

    # Map position IDs to names
    position_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    players_df['position'] = players_df['element_type'].map(position_map)

    # Select and rename columns to match the new schema
    players_df = players_df[['id', 'full_name', 'position', 'team']]
    players_df = players_df.rename(columns={'id': 'player_id', 'team': 'team_id'})

    # Insert players
    players_to_insert = players_df.to_dict(orient='records')
    cursor.executemany(
        "INSERT OR REPLACE INTO players (player_id, full_name, position, team_id) VALUES (:player_id, :full_name, :position, :team_id)",
        players_to_insert
    )

    conn.commit()
    conn.close()