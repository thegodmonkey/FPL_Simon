## Project Goal
FPL Simon is a web application that provides fantasy football advice by analyzing data from the Fantasy Premier League (FPL) API and other sources like fbref. It uses Python libraries to pull and store data, and an LLM to generate insights and recommendations. It will also be used as a personal test & learning opportunity for LLM Evals.

## Current Status
The project has a functional backend data pipeline. Data is successfully ingested from the FPL and FBRef APIs, stored in a local SQLite database with a robust relational schema, and exposed via a basic Flask API. The project is well-tested and has an automated PR review process.

## Next Steps
The immediate focus is on implementing the AI analysis layer and building out the API to support the frontend.
1.  **Refactor `populate_fbref_stats`**: Update the function in `api/database.py` to align with the current, superior database schema. This requires mapping `soccerdata` column names and looking up `player_id`.
2.  **Implement `analysis.py`**: Build the `get_llm_insight` function to query the database for player data and send it to a Gemini model for analysis.
3.  **Create Insight Endpoint**: Add a new API endpoint in `api/app.py` that uses the analysis module to return AI-generated advice for a specific player.
4.  **Develop Frontend**: Begin building the React components to display players and their associated insights.

## Technology Stack
- **Backend**: Python (with Flask for the API)
- **Data Fetching**: `fpl` library (for FPL API), `soccerdata` (for fbref)
- **Database**: SQLite
- **AI**: Google Gemini
- **Frontend**: React

## File Structure
- **/api**: Contains the Python backend.
  - `app.py`: The main Flask application file that defines API endpoints.
  - `data_fetcher.py`: Module responsible for all external data ingestion (FPL API, fbref).
  - `database.py`: Module to handle all database interactions (connecting, creating tables, inserting/querying data).
  - `analysis.py`: Contains the logic for interacting with the Gemini LLM to generate insights.
  - `requirements.txt`: Lists all Python package dependencies.
- **/frontend**: Contains the React frontend application.
- `tests/`: Contains all tests for the backend.