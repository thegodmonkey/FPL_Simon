from flask import Flask, jsonify
from .database import get_db_connection
from .analysis import get_llm_insight

app = Flask(__name__)

@app.route('/api/players')
def get_players():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM players')
            players = cursor.fetchall()

        return jsonify([dict(player) for player in players])
    finally:
        if conn:
            conn.close()

@app.route('/api/stats/<int:player_id>')
def get_player_stats(player_id):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM player_stats_fbref WHERE player_id = ?', (player_id,))
            stats = cursor.fetchall()

        return jsonify([dict(row) for row in stats])
    finally:
        if conn:
            conn.close()

@app.route('/api/players/<int:player_id>/insight')
def get_player_insight(player_id):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # Fetch player details
            cursor.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
            player = cursor.fetchone()

            if not player:
                return jsonify({"error": "Player not found"}), 404

            player_dict = dict(player)

            # Fetch team name
            cursor.execute('SELECT team_name FROM teams WHERE team_id = ?', (player_dict['team_id'],))
            team = cursor.fetchone()
            team_name = dict(team)['team_name'] if team else "Unknown"

            # Fetch player stats
            cursor.execute('SELECT * FROM player_stats_fbref WHERE player = ?', (player_dict['full_name'],))
            stats = cursor.fetchall()
            stats_list = [dict(row) for row in stats]

            # Construct prompt and context
            prompt = "show me the player name, team and key stats based on the information provided"
            context = f"""
            Player: {player_dict['full_name']}
            Team: {team_name}
            Stats: {stats_list}
            """

            insight = get_llm_insight(prompt=prompt, context=context)
            return jsonify({"insight": insight})
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
