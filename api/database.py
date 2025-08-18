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
                player_id INTEGER,
                league TEXT, season TEXT, team TEXT, nation TEXT, pos TEXT, age REAL, born REAL,
                "Playing Time_MP" REAL, "Playing Time_Starts" REAL, "Playing Time_Min" REAL, "Playing Time_90s" REAL,
                "Performance_Gls" REAL, "Performance_Ast" REAL, "Performance_G+A" REAL, "Performance_G-PK" REAL,
                "Performance_PK" REAL, "Performance_PKatt" REAL, "Performance_CrdY" REAL, "Performance_CrdR" REAL,
                "Expected_xG" REAL, "Expected_npxG" REAL, "Expected_xAG" REAL, "Expected_npxG+xAG" REAL,
                "Progression_PrgC" REAL, "Progression_PrgP" REAL, "Progression_PrgR" REAL,
                "Per 90 Minutes_Gls" REAL, "Per 90 Minutes_Ast" REAL, "Per 90 Minutes_G+A" REAL,
                "Per 90 Minutes_G-PK" REAL, "Per 90 Minutes_G+A-PK" REAL, "Per 90 Minutes_xG" REAL,
                "Per 90 Minutes_xAG" REAL, "Per 90 Minutes_xG+xAG" REAL, "Per 90 Minutes_npxG" REAL,
                "Per 90 Minutes_npxG+xAG" REAL,
                PRIMARY KEY (player_id, league, season, team),
                FOREIGN KEY (player_id) REFERENCES players (player_id)
            )
        ''')

        conn.commit()

def populate_fbref_stats(stats_dataframe: pd.DataFrame):
    """
    Populates the player_stats_fbref table from a DataFrame.
    This function maps player names to IDs, unnests the multi-level column index,
    and inserts the data into the database.
    """
    with get_db_connection() as conn:
        # Step 1: Create a mapping from full_name to player_id from the players table.
        players_map_df = pd.read_sql_query("SELECT player_id, full_name FROM players", conn)
        player_name_to_id = players_map_df.set_index('full_name')['player_id'].to_dict()

    # Step 2: Prepare the stats DataFrame
    # Reset the index to turn 'league', 'season', 'team', 'player' from index to columns.
    stats_dataframe.reset_index(inplace=True)
    # Flatten the MultiIndex columns (e.g., ('Performance', 'Gls') -> 'Performance_Gls').
    if isinstance(stats_dataframe.columns, pd.MultiIndex):
        stats_dataframe.columns = ['_'.join(col).strip('_') for col in stats_dataframe.columns.values]

    # Step 3: Map player names to player_id.
    stats_dataframe['player_id'] = stats_dataframe['player'].map(player_name_to_id)

    # Log and remove rows where the player name couldn't be mapped to an ID.
    unmapped_players = stats_dataframe[stats_dataframe['player_id'].isnull()]
    if not unmapped_players.empty:
        logging.warning(f"Could not find player_id for the following players: {unmapped_players['player'].unique().tolist()}")
    stats_dataframe.dropna(subset=['player_id'], inplace=True)
    stats_dataframe['player_id'] = stats_dataframe['player_id'].astype(int)

    # Step 4: Filter DataFrame to only include columns that exist in the database table.
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(player_stats_fbref)")
        table_columns = {info[1] for info in cursor.fetchall()}

    # We no longer need the 'player' name column for insertion.
    if 'player' in stats_dataframe.columns:
        stats_dataframe.drop(columns=['player'], inplace=True)

    df_filtered = stats_dataframe[[col for col in stats_dataframe.columns if col in table_columns]]

    # Step 5: Insert data into the database.
    with get_db_connection() as conn:
        try:
            # Use a custom method for 'INSERT OR REPLACE' functionality with pandas `to_sql`.
            # The PRIMARY KEY on (player_id, league, season, team) ensures uniqueness.
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

def get_player_data(player_id: int) -> pd.DataFrame:
    """
    Retrieves all data for a specific player from the database.

    Args:
        player_id: The ID of the player to retrieve data for.

    Returns:
        A pandas DataFrame containing the player's data.
    """
    with get_db_connection() as conn:
        # This query joins the players table with their stats, filtering by player_id.
        # It uses a subquery to get the player's full name from their ID,
        # then joins with the stats table on that name.
        query = """
            SELECT *
            FROM players p
            LEFT JOIN player_stats_fbref s USING(player_id)
            WHERE p.player_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(player_id,))
    return df