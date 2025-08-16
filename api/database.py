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
            player_id INTEGER,
            season TEXT,
            minutes_per_90 REAL,
            xg_per_90 REAL,
            xa_per_90 REAL,
            goals INTEGER,
            assists INTEGER,
            g_minus_pk REAL,
            pk INTEGER,
            pk_att INTEGER,
            crdy INTEGER,
            crdr INTEGER,
            sh INTEGER,
            sot INTEGER,
            sot_percent REAL,
            sh_per_90 REAL,
            sot_per_90 REAL,
            g_per_sh REAL,
            g_per_sot REAL,
            dist REAL,
            fk INTEGER,
            npxg REAL,
            cmp INTEGER,
            att_pass INTEGER,
            cmp_percent REAL,
            tot_dist INTEGER,
            prg_dist INTEGER,
            cmp_short INTEGER,
            att_short INTEGER,
            cmp_percent_short REAL,
            cmp_medium INTEGER,
            att_medium INTEGER,
            cmp_percent_medium REAL,
            cmp_long INTEGER,
            att_long INTEGER,
            cmp_percent_long REAL,
            ast INTEGER,
            xa REAL,
            a_minus_xa REAL,
            kp INTEGER,
            one_third INTEGER,
            ppa INTEGER,
            crspa INTEGER,
            prog_pass INTEGER,
            sca INTEGER,
            sca90 REAL,
            gca INTEGER,
            gca90 REAL,
            tkl INTEGER,
            tklw INTEGER,
            def_3rd_tkl INTEGER,
            mid_3rd_tkl INTEGER,
            att_3rd_tkl INTEGER,
            tkl_vs_dribblers INTEGER,
            att_vs_dribblers INTEGER,
            tkl_percent_vs_dribblers REAL,
            past_dribbled INTEGER,
            blocks INTEGER,
            sh_blocked INTEGER,
            pass_blocked INTEGER,
            interceptions INTEGER,
            tkl_plus_int INTEGER,
            clr INTEGER,
            err INTEGER,
            touches INTEGER,
            def_pen_touches INTEGER,
            def_3rd_touches INTEGER,
            mid_3rd_touches INTEGER,
            att_3rd_touches INTEGER,
            att_pen_touches INTEGER,
            live_touches INTEGER,
            succ_dribbles INTEGER,
            att_dribbles INTEGER,
            succ_percent_dribbles REAL,
            num_pl_dribbled_past INTEGER,
            megs INTEGER,
            carries INTEGER,
            tot_dist_carries INTEGER,
            prg_dist_carries INTEGER,
            prog_carries INTEGER,
            one_third_carries INTEGER,
            cpa_carries INTEGER,
            mis_carries INTEGER,
            dis_carries INTEGER,
            rec_passes INTEGER,
            prog_rec_passes INTEGER,
            crdy_misc INTEGER,
            crdr_misc INTEGER,
            two_crdy INTEGER,
            fld INTEGER,
            fls INTEGER,
            off INTEGER,
            crs INTEGER,
            int_misc INTEGER,
            tklw_misc INTEGER,
            pkwon INTEGER,
            pkcon INTEGER,
            og INTEGER,
            recov INTEGER,
            FOREIGN KEY (player_id) REFERENCES players (player_id),
            PRIMARY KEY (player_id, season)
        )
    ''')

    conn.commit()
    conn.close()

def populate_fbref_stats(stats_dataframe):
    """
    Populates the player_stats_fbref table from a DataFrame.
    """
    conn = get_db_connection()

    # A comprehensive mapping from potential DataFrame column names to sanitized DB column names
    column_mapping = {
        'G-PK': 'g_minus_pk', 'PKatt': 'pk_att', 'CrdY': 'crdy', 'CrdR': 'crdr',
        'Sh': 'sh', 'SoT': 'sot', 'SoT%': 'sot_percent', 'Sh/90': 'sh_per_90',
        'SoT/90': 'sot_per_90', 'G/Sh': 'g_per_sh', 'G/SoT': 'g_per_sot',
        'Dist': 'dist', 'FK': 'fk', 'npxG': 'npxg', 'Cmp': 'cmp', 'Att': 'att_pass',
        'Cmp%': 'cmp_percent', 'TotDist': 'tot_dist', 'PrgDist': 'prg_dist',
        'Cmp (Short)': 'cmp_short', 'Att (Short)': 'att_short', 'Cmp% (Short)': 'cmp_percent_short',
        'Cmp (Medium)': 'cmp_medium', 'Att (Medium)': 'att_medium', 'Cmp% (Medium)': 'cmp_percent_medium',
        'Cmp (Long)': 'cmp_long', 'Att (Long)': 'att_long', 'Cmp% (Long)': 'cmp_percent_long',
        'Ast': 'ast', 'xA': 'xa', 'A-xA': 'a_minus_xa', 'KP': 'kp', '1/3': 'one_third',
        'PPA': 'ppa', 'CrsPA': 'crspa', 'Prog': 'prog_pass', 'SCA': 'sca', 'SCA90': 'sca90',
        'GCA': 'gca', 'GCA90': 'gca90', 'Tkl': 'tkl', 'TklW': 'tklw', 'Def 3rd': 'def_3rd_tkl',
        'Mid 3rd': 'mid_3rd_tkl', 'Att 3rd': 'att_3rd_tkl', 'Tkl (vs Dribblers)': 'tkl_vs_dribblers',
        'Att (vs Dribblers)': 'att_vs_dribblers', 'Tkl% (vs Dribblers)': 'tkl_percent_vs_dribblers',
        'Past': 'past_dribbled', 'Blocks': 'blocks', 'Sh Blocked': 'sh_blocked',
        'Pass Blocked': 'pass_blocked', 'Int': 'interceptions', 'Tkl+Int': 'tkl_plus_int',
        'Clr': 'clr', 'Err': 'err', 'Touches': 'touches', 'Def Pen': 'def_pen_touches',
        'Def 3rd Touches': 'def_3rd_touches', 'Mid 3rd Touches': 'mid_3rd_touches',
        'Att 3rd Touches': 'att_3rd_touches', 'Att Pen': 'att_pen_touches', 'Live': 'live_touches',
        'Succ': 'succ_dribbles', 'Att (Dribbles)': 'att_dribbles', 'Succ%': 'succ_percent_dribbles',
        '#Pl': 'num_pl_dribbled_past', 'Megs': 'megs', 'Carries': 'carries',
        'TotDist (Carries)': 'tot_dist_carries', 'PrgDist (Carries)': 'prg_dist_carries',
        'Prog (Carries)': 'prog_carries', '1/3 (Carries)': 'one_third_carries',
        'CPA (Carries)': 'cpa_carries', 'Mis (Carries)': 'mis_carries',
        'Dis (Carries)': 'dis_carries', 'Rec': 'rec_passes', 'Prog (Rec)': 'prog_rec_passes',
        '2CrdY': 'two_crdy', 'Fld': 'fld', 'Fls': 'fls', 'Off': 'off', 'Crs': 'crs',
        'PKwon': 'pkwon', 'PKcon': 'pkcon', 'OG': 'og', 'Recov': 'recov',
        # Adding some variations observed in data sources
        'Passes Cmp': 'cmp', 'Passes Att': 'att_pass', 'Passes Cmp%': 'cmp_percent',
        'Tackles TklW': 'tklw', 'Dribbles Succ': 'succ_dribbles', 'Dribbles Att': 'att_dribbles',
        'Goals': 'goals', 'Assists': 'assists', 'xG': 'xg_per_90', 'xAG': 'xa_per_90'
    }
    stats_dataframe.rename(columns=column_mapping, inplace=True)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(player_stats_fbref)")
    table_columns = {info[1] for info in cursor.fetchall()}

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