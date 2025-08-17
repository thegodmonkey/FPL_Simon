import os
import pandas as pd
import google.generativeai as genai
from . import database

# Configure the generative AI model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_llm_insight(player_id: int):
    """
    Generates insights from a Large Language Model (LLM) for a given player.

    Args:
        player_id: The ID of the player to analyze.

    Returns:
        A string containing the LLM's generated insight, or an error message.
    """
    # Retrieve player data from the database
    player_data = database.get_player_data(player_id)
    if player_data.empty:
        return f"No data found for player with ID {player_id}."

    # Format the data into a context string
    # Convert the DataFrame to a string, which is a simple way to represent the data.
    context = player_data.to_string()

    # Create a prompt for the FPL expert
    prompt = f"""
    You are an expert Fantasy Premier League (FPL) analyst.
    Please provide a detailed analysis of the following player based on their data.
    Include insights on their recent performance, scoring potential, and value for money.
    Conclude with a clear recommendation on whether to include them in an FPL squad.

    Player Data:
    {context}
    """

    # Generate the insight using the Gemini API
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the LLM insight: {e}"
