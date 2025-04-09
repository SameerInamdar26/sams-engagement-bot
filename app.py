import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import asyncio
import threading
import random
import time
from playwright.sync_api import sync_playwright

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)"
]

PROXIES = [
    "http://51.158.68.68:8811",
    "http://185.199.229.156:7492",
    "http://195.154.255.194:80"
]

DEFAULT_COMMENTS = [
    "Amazing video!",
    "Keep up the good work!",
    "Loved it ❤️",
    "Awesome content!",
    "Subbed!"
]

@app.route('/')
def index():
    return render_template('dashboard.html')

@socketio.on('start_bots')
def handle_start_bots(data):
    print("✅ Received bot request:", data)

    def run_bots():
        video_url = data['video_url']
        total_bots = int(data['total_bots'])
        batch_size = int(data['batch_size'])
        actions = data.get('actions', [])
        custom_comments = data.get('custom_comments', [])

        for i in range(1, total_bots + 1):
            bot_id = f"Bot {i}"
            try:
                proxy = random.choice(PROXIES)
                user_agent = random.choice(USER_AGENTS)
                comment_text = random.choice(custom_comments) if custom_comments else random.choice(DEFAULT_COMMENTS)

                # Launch each bot in Playwright
                launch_bot(bot_id, video_url, actions, proxy, user_agent, comment_text)

                socketio.emit('progress_update', {'progress': int(i / total_bots * 100)})
            except Exception as e:
                print(f"❌ {bot_id} failed:", e)
                continue
            eventlet.sleep(0.3)

        socketio.emit('bot_done', {'status': '✅ All bots done!'})

    threading.Thread(target=run_bots).start()

def launch_bot(bot_id, video_url, actions, proxy, user_agent, comment_text):
    print(f"🚀 {bot_id} starting with proxy: {proxy} | UA: {user_agent}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, proxy={"server": proxy})
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        page.goto(video_url, timeout=60000)
        page.wait_for_timeout(5000)  # Let the page load

        if "view" in actions:
            print(f"👁️ {bot_id} viewed the video")
            page.wait_for_timeout(10000)  # Simulate watching

        if "like" in actions:
            try:
                page.click('button[aria-label*="like"]')
                print(f"👍 {bot_id} liked the video")
            except:
                print(f"⚠️ {bot_id} could not like")

        if "subscribe" in actions:
            try:
                page.click('button:has-text("Subscribe")')
                print(f"🔔 {bot_id} subscribed")
            except:
                print(f"⚠️ {bot_id} could not subscribe")

        if "share" in actions:
            print(f"📤 {bot_id} shared the video (simulated)")

        if "comment" in actions:
            try:
                page.fill('textarea', comment_text)
                page.keyboard.press('Enter')
                print(f"💬 {bot_id} commented: {comment_text}")
            except:
                print(f"⚠️ {bot_id} could not comment")

        context.close()
        browser.close()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
