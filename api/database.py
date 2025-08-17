import sqlite3
import pandas as pd
import logging

DATABASE_FILE = 'fpl.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_database_tables():
    """Initializes the database and creates tables if they don't exist."""
    with get_db_connection() as conn:
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

def populate_fbref_stats(stats_dataframe: pd.DataFrame):
    """
    Populates the player_stats_fbref table from a DataFrame.

    This function handles the transformation of a multi-indexed DataFrame from soccerdata
    into a format suitable for our SQLite database.
    """
    # The soccerdata library returns a DataFrame with a multi-level index (e.g., ('league', ''), ('season', '')).
    # We reset the index to convert the indexed fields ('league', 'season', 'team', 'player') into regular columns.
    stats_dataframe.reset_index(inplace=True)

    # The column headers are also a MultiIndex, e.g., ('Performance', 'Gls').
    # We flatten this into a single-level index by joining the levels with an underscore,
    # resulting in a column name like 'Performance_Gls'.
    if isinstance(stats_dataframe.columns, pd.MultiIndex):
        stats_dataframe.columns = ['_'.join(col).strip('_') for col in stats_dataframe.columns.values]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # To prevent errors from schema mismatches, we fetch the actual column names from the database table.
        cursor.execute("PRAGMA table_info(player_stats_fbref)")
        table_columns = {info[1] for info in cursor.fetchall()}

        # We then filter the DataFrame, keeping only the columns that exist in the target table.
        # This makes the function more robust against changes in the data source.
        df_filtered = stats_dataframe[[col for col in stats_dataframe.columns if col in table_columns]]

        # A transaction is used to ensure the integrity of the data.
        # The whole operation will be rolled back if any part of it fails.
        try:
            # The `to_sql` method from pandas is used for bulk insertion.
            # We define a custom `insert_or_replace` method to handle cases where a player's stats
            # for a given season already exist in the table. The PRIMARY KEY on (league, season, team, player)
            # ensures uniqueness.
            def insert_or_replace(table, connection, keys, data_iter):
                sql = f'INSERT OR REPLACE INTO "{table.name}" ({",".join(f"`{k}`" for k in keys)}) VALUES ({",".join(["?"] * len(keys))})'
                connection.executemany(sql, data_iter)

            df_filtered.to_sql(
                'player_stats_fbref',
                conn,
                if_exists='append',  # Use 'append' with our custom method to get insert-or-replace behavior.
                index=False,
                chunksize=1000,      # Process the data in chunks to manage memory usage.
                method=insert_or_replace
            )

            conn.commit()
        except Exception as e:
            logging.error(f"An error occurred during database population: {e}")
            conn.rollback()
            raise

def populate_teams_and_players(players_data, teams_data):
    """
    Populates the teams and players tables from the FPL player data, mapping to the new schema.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # --- Teams Population ---
        # We use 'INSERT OR IGNORE' for teams because the team data is static and unlikely to change.
        # If a team already exists in the table, we simply ignore the new entry.
        teams_df = pd.DataFrame(teams_data)
        teams_df = teams_df[['id', 'name', 'code']]
        teams_df = teams_df.rename(columns={'id': 'team_id', 'name': 'team_name', 'code': 'fpl_team_code'})
        teams_to_insert = teams_df.to_dict(orient='records')
        cursor.executemany(
            "INSERT OR IGNORE INTO teams (team_id, team_name, fpl_team_code) VALUES (:team_id, :team_name, :fpl_team_code)",
            teams_to_insert
        )

        # --- Players Population ---
        # We use 'INSERT OR REPLACE' for players. This is because player details (like their team) can change.
        # If a player with the same player_id already exists, this command will update their record.
        players_df = pd.DataFrame(players_data)
        # Create full_name from first and last names.
        players_df['full_name'] = players_df['first_name'] + ' ' + players_df['second_name']

        # Map FPL's numeric position IDs to human-readable position names.
        position_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
        players_df['position'] = players_df['element_type'].map(position_map)

        # Select and rename columns to match our database schema.
        players_df = players_df[['id', 'full_name', 'position', 'team']]
        players_df = players_df.rename(columns={'id': 'player_id', 'team': 'team_id'})

        # Insert player data into the 'players' table.
        players_to_insert = players_df.to_dict(orient='records')
        cursor.executemany(
            "INSERT OR REPLACE INTO players (player_id, full_name, position, team_id) VALUES (:player_id, :full_name, :position, :team_id)",
            players_to_insert
        )

        conn.commit()