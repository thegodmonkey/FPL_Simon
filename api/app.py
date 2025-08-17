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
    insight = get_llm_insight(prompt=str(player_id), context=str(player_id))
    return jsonify({"insight": insight})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
