# FPL Simon

## Project Goal
FPL Simon is a web application that provides fantasy football advice by analyzing data from the Fantasy Premier League (FPL) API and other sources like fbref or trusted twitter accounts. It uses APIs or libraries to pull in data and an LLM to generate insights and recommendations. It will be also used as a personal test & learning opportunity for LLM Evals.

## File Structure
- **backend/server.js**: The main entry point for the Node.js server.
- **backend/fplService.js**: Module to fetch data from the FPL API.
- **backend/fbrefService.js**: Module for fetching data from fbref.
- **backend/dataStore.js**: Handles storing and retrieving data.
- **frontend/**: Contains the React frontend application.