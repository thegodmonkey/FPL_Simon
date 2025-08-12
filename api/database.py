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
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Create players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')

    conn.commit()
    conn.close()

def populate_teams_and_players(players_data, teams_data):
    """
    Populates the teams and players tables from the FPL player data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create a DataFrame for teams and insert them
    teams_df = pd.DataFrame([team.__dict__ for team in teams_data])
    teams_df = teams_df[['id', 'name']]
    teams_to_insert = teams_df.to_dict(orient='records')
    cursor.executemany("INSERT OR IGNORE INTO teams (id, name) VALUES (:id, :name)", teams_to_insert)

    # Create a DataFrame for players
    players_df = pd.DataFrame([player.__dict__ for player in players_data])
    players_df = players_df[['id', 'web_name', 'element_type', 'team']]
    players_df = players_df.rename(columns={'web_name': 'name', 'element_type': 'position', 'team': 'team_id'})

    # Map position IDs to names
    position_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
    players_df['position'] = players_df['position'].map(position_map)

    # Insert players
    players_to_insert = players_df.to_dict(orient='records')
    cursor.executemany("INSERT OR REPLACE INTO players (id, name, position, team_id) VALUES (:id, :name, :position, :team_id)", players_to_insert)

    conn.commit()
    conn.close()
