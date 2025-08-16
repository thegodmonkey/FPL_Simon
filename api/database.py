import sqlite3
import pandas as pd
import logging

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

    # Create player_stats_fbref table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats_fbref (
            league TEXT, season TEXT, team TEXT, player TEXT, nation TEXT, pos TEXT, age REAL, born REAL,
            "Playing Time_MP" REAL, "Playing Time_Starts" REAL, "Playing Time_Min" REAL, "Playing Time_90s" REAL,
            "Performance_Gls" REAL, "Performance_Ast" REAL, "Performance_G+A" REAL, "Performance_G-PK" REAL,
            "Performance_PK" REAL, "Performance_PKatt" REAL, "Performance_CrdY" REAL, "Performance_CrdR" REAL,
            "Expected_xG" REAL, "Expected_npxG" REAL, "Expected_xAG" REAL, "Expected_npxG+xAG" REAL,
            "Progression_PrgC" REAL, "Progression_PrgP" REAL, "Progression_PrgR" REAL,
            "Per 90 Minutes_Gls" REAL, "Per 90 Minutes_Ast" REAL, "Per 90 Minutes_G+A" REAL,
            "Per 90 Minutes_G-PK" REAL, "Per 90 Minutes_G+A-PK" REAL, "Per 90 Minutes_xG" REAL,
            "Per 90 Minutes_xAG" REAL, "Per 90 Minutes_xG+xAG" REAL, "Per 90 Minutes_npxG" REAL,
            "Per 90 Minutes_npxG+xAG" REAL,
            PRIMARY KEY (league, season, team, player)
        )
    ''')

    conn.commit()
    conn.close()

def populate_fbref_stats(stats_dataframe: pd.DataFrame):
    """
    Populates the player_stats_fbref table from a DataFrame.
    """
    conn = get_db_connection()

    # The soccerdata library returns a DataFrame with a multi-level index.
    # We reset it so that 'league', 'season', 'team', and 'player' become columns.
    stats_dataframe.reset_index(inplace=True)

    # Flatten the MultiIndex columns, e.g., ('Performance', 'Gls') becomes 'Performance_Gls'
    # We also strip leading/trailing underscores that might result from empty names in the MultiIndex.
    if isinstance(stats_dataframe.columns, pd.MultiIndex):
        stats_dataframe.columns = ['_'.join(col).strip('_') for col in stats_dataframe.columns.values]

    cursor = conn.cursor()
    # Use PRAGMA to get the columns of the target table
    cursor.execute("PRAGMA table_info(player_stats_fbref)")
    table_columns = {info[1] for info in cursor.fetchall()}

    # Filter the DataFrame to only include columns that exist in the database table
    # This is a defensive measure to avoid errors if the source data changes.
    df_filtered = stats_dataframe[[col for col in stats_dataframe.columns if col in table_columns]]

    # Use a transaction for the insert/update operation
    try:
        # Since we have a primary key on (league, season, team, player),
        # we can use INSERT OR REPLACE to handle duplicates.
        def insert_or_replace(table, connection, keys, data_iter):
            sql = f'INSERT OR REPLACE INTO "{table.name}" ({",".join(f"`{k}`" for k in keys)}) VALUES ({",".join(["?"] * len(keys))})'
            connection.executemany(sql, data_iter)

        df_filtered.to_sql(
            'player_stats_fbref',
            conn,
            if_exists='append',
            index=False,
            chunksize=1000,
            method=insert_or_replace
        )
        
        conn.commit()
    except Exception as e:
        logging.error(f"An error occurred during database population: {e}")
        conn.rollback()
        raise
    finally:
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