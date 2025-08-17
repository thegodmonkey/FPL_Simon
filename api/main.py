import logging
from database import create_database_tables, populate_teams_and_players, populate_fbref_stats
from data_fetcher import get_fpl_data, get_fbref_stats

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to initialize the database and populate it with FPL and FBref data.
    """
    try:
        logging.info("Initializing the database...")
        create_database_tables()
        logging.info("Database initialized.")

        logging.info("Fetching FPL data...")
        players_data, teams_data = get_fpl_data()
        logging.info("FPL data fetched.")

        season = "2024-2025"  # This could be parameterized or moved to a config file.
        logging.info(f"Fetching FBref stats data for the {season} season...")
        stats_df = get_fbref_stats(season=season)

        logging.info("Populating the database with FPL teams and players data...")
        populate_teams_and_players(players_data, teams_data)
        logging.info("Database populated with FPL data successfully.")

        logging.info("Populating the database with FBref stats data...")
        populate_fbref_stats(stats_df)
        logging.info("Database populated with FBref stats successfully.")

    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}", exc_info=True)

if __name__ == "__main__":
    main()
