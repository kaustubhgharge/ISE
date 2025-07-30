import sqlite3
from flask import Flask, jsonify, render_template, request
import threading
import time
import random

app = Flask(__name__)

DB_PATH = 'bins.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # So we can access columns by name
    return conn

def update_bin_statuses(thresholds):
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    for bin in bins:
        status = 'ok'
        if bin['last_emptied_days_ago'] > thresholds['inactive']:
            status = 'inactive'
        elif bin['fill'] >= thresholds['full']:
            status = 'full'
        elif bin['fill'] >= thresholds['nearly_full']:
            status = 'nearly_full'
        # Update status in DB
        conn.execute('UPDATE bins SET status = ? WHERE id = ?', (status, bin['id']))
    conn.commit()
    conn.close()

def randomize_fill_levels():
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM bins WHERE type != "HUB"').fetchall()
    for bin in bins:
        new_fill = random.randint(0, 100)
        conn.execute('UPDATE bins SET fill = ? WHERE id = ?', (new_fill, bin['id']))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/bins')
def get_bins():
    thresholds = {
        'full': int(request.args.get('full', 80)),
        'nearly_full': int(request.args.get('nearly_full', 60)),
        'inactive': int(request.args.get('inactive', 5))
    }
    update_bin_statuses(thresholds)
    conn = get_db_connection()
    bins = conn.execute('SELECT * FROM bins').fetchall()
    bins_list = [dict(bin) for bin in bins]
    conn.close()
    return jsonify(bins_list)

@app.route('/api/collect', methods=['POST'])
def collect_bins():
    bin_ids = request.json.get('bin_ids', [])
    conn = get_db_connection()
    for bin_id in bin_ids:
        conn.execute('''
            UPDATE bins SET fill = 0, last_emptied_days_ago = 0, status = 'ok' WHERE id = ?
        ''', (bin_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bins collected and reset'})

@app.route('/api/optimized_route')
def get_route():
    conn = get_db_connection()
    hub = conn.execute('SELECT * FROM bins WHERE type = "HUB"').fetchone()
    if not hub:
        return jsonify({'error': 'HUB not found'}), 400

    to_visit = conn.execute('''
        SELECT * FROM bins WHERE status IN ("full", "nearly_full", "inactive") AND type != "HUB"
    ''').fetchall()

    path = [[hub['lat'], hub['lon']]] + [[b['lat'], b['lon']] for b in to_visit] + [[hub['lat'], hub['lon']]]

    conn.close()
    return jsonify({'path': path})

@app.route('/bin/<int:bin_id>')
def bin_detail(bin_id):
    conn = get_db_connection()
    bin_data = conn.execute('SELECT * FROM bins WHERE id = ?', (bin_id,)).fetchone()
    conn.close()
    if not bin_data or bin_data['type'] == 'HUB':
        return "Bin not found", 404
    return render_template('bin_detail.html', bin=bin_data)

def auto_randomize_fill():
    while True:
        randomize_fill_levels()
        time.sleep(30)

if __name__ == '__main__':
    threading.Thread(target=auto_randomize_fill, daemon=True).start()
    app.run(debug=True)
