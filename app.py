from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from bot import run_bot  # Assuming you have a bot.py with run_bot function

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')  # 'eventlet' or 'gevent' can break on Render

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/start-bot', methods=['POST'])
def start_bot():
    data = request.get_json()
    video_url = data['video_url']
    total_bots = int(data['total_bots'])
    batch_size = int(data['batch_size'])
    actions = data['actions']  # e.g., ['view', 'like']

    def bot_task():
        run_bot(video_url, total_bots, batch_size, actions, socketio)

    threading.Thread(target=bot_task).start()
    return jsonify({'status': 'Bot started'})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('progress', {'data': 'Connected to server'})

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
