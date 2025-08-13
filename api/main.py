from database import init_db, populate_teams_and_players
from data_fetcher import get_fpl_data

def main():
    """
    Main function to initialize the database and populate it with FPL data.
    """
    print("Initializing the database...")
    init_db()
    print("Database initialized.")

    print("Fetching FPL data...")
    players_data, teams_data = get_fpl_data()
    print("FPL data fetched.")

    print("Populating the database with teams and players data...")
    populate_teams_and_players(players_data, teams_data)
    print("Database populated successfully.")

if __name__ == "__main__":
    main()
