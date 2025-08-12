import sqlite3

def create_database_tables():
    """
    Connects to the database and creates the 'teams' and 'players' tables.
    """
    conn = sqlite3.connect('api/fpl_data.db')
    cursor = conn.cursor()

    # Create the teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT NOT NULL,
        fpl_team_code INTEGER
    )
    ''')

    # Create the players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        position TEXT,
        current_team_id INTEGER,
        FOREIGN KEY (current_team_id) REFERENCES teams(team_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")
