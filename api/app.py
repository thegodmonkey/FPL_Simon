from flask import Flask, jsonify
from .database import get_db_connection

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
