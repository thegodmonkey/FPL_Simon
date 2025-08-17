# FPL Simon

FPL Simon is a web application that provides fantasy football advice by analyzing data from the Fantasy Premier League (FPL) API and other sources like fbref. It uses Python libraries to pull and store data, and a generative AI model to generate insights and recommendations.

## Technology Stack

- **Backend**: Python with Flask for the API
- **Data Fetching**:
    - `fpl` library for the FPL API
    - `soccerdata` for fbref
- **Database**: SQLite
- **AI**: Google Generative AI

## File Structure

- **/api**: Contains the Python backend.
  - `app.py`: The main Flask application file that defines API endpoints.
  - `main.py`: A script to initialize and populate the database.
  - `data_fetcher.py`: Module responsible for all external data ingestion.
  - `database.py`: Module to handle all database interactions.
  - `analysis.py`: Contains the logic for interacting with the generative AI model.
  - `requirements.txt`: Lists all Python package dependencies.
- `tests/`: Contains all tests for the backend.
- `.github/`: Contains GitHub Actions workflows.

## Setup and Running

1.  **Install dependencies:**

    ```bash
    pip install -r api/requirements.txt
    ```

2.  **Initialize the database:**

    This will create the `fpl.db` file and populate it with data from the FPL and fbref APIs.

    ```bash
    python api/main.py
    ```

3.  **Run the API server:**

    ```bash
    flask --app api/app.py run
    ```

    The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

-   **GET /api/players**

    Returns a list of all players in the database.

-   **GET /api/stats/<player_id>**

    Returns the fbref stats for a specific player.