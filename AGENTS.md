## Project Goal
FPL Simon is a web application that provides fantasy football advice by analyzing data from the Fantasy Premier League (FPL) API and other sources like fbref. It uses Python libraries to pull and store data, and an LLM to generate insights and recommendations. It will also be used as a personal test & learning opportunity for LLM Evals.

## Technology Stack
- **Backend**: Python (with Flask or FastAPI for the API)
- **Data Fetching**: `fpl` library (for FPL API), `soccerdata` (for fbref)
- **Database**: SQLite
- **Frontend**: React

## File Structure
- **/api**: Contains the Python backend.
  - `app.py`: The main Flask/FastAPI application file that defines API endpoints.
  - `data_fetcher.py`: Module responsible for all external data ingestion (FPL API, fbref via `soccerdata`).
  - `database.py`: Module to handle all database interactions (connecting, creating tables, inserting/querying data).
  - `analysis.py`: Contains the logic for interacting with the LLM to generate insights.
  - `requirements.txt`: Lists all Python package dependencies.
- **/frontend**: Contains the React frontend application.
- `tests/`: Contains all tests for the backend.
  - `test_data_fetcher.py`: Unit tests for the data ingestion functions.
  - `test_database.py`: Tests for the database logic.