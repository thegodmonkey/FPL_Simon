from database import init_db, populate_teams_and_players, populate_fbref_stats
from data_fetcher import get_fpl_data, get_fbref_stats

def main():
    """
    Main function to initialize the database and populate it with FPL and FBref data.
    """
    print("Initializing the database...")
    init_db()
    print("Database initialized.")

    print("Fetching FPL data...")
    players_data, teams_data = get_fpl_data()
    print("FPL data fetched.")

    season = "2024-2025" # Or get from config/args
    print(f"Fetching FBref stats data for the {season} season...")
    stats_df = get_fb_ref_stats(season=season)
    populate_teams_and_players(players_data, teams_data)
    print("Database populated with FPL data successfully.")

    print("Populating the database with FBref stats data...")
    populate_fbref_stats(stats_df)
    print("Database populated with FBref stats successfully.")

if __name__ == "__main__":
    main()
