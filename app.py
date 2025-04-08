from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import asyncio
import threading
from bot import run_bot

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')


@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/run-bots', methods=['POST'])
def run_bots():
    data = request.json
    url = data['url']
    total_bots = int(data['total_bots'])
    batch_size = int(data['batch_size'])
    actions = data['actions']

    threading.Thread(target=start_bots, args=(url, total_bots, batch_size, actions)).start()

    return jsonify({'status': 'started'})

def start_bots(url, total_bots, batch_size, actions):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    total = total_bots
    done = 0

    async def run_batch():
        nonlocal done
        for i in range(0, total_bots, batch_size):
            tasks = []
            for j in range(min(batch_size, total_bots - i)):
                bot_id = i + j + 1
                socketio.emit('log', f'🚀 Bot {bot_id} started')
                tasks.append(run_bot(url, actions, bot_id))
            await asyncio.gather(*tasks)
            done += len(tasks)
            socketio.emit('progress', {'done': done, 'total': total})
        socketio.emit('log', '✅ All bots completed')

    loop.run_until_complete(run_batch())

if __name__ == '__main__':
    socketio.run(app, debug=True)
