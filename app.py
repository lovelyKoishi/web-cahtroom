# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, emit
import time
import uuid
from markupsafe import escape
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey123!'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio = SocketIO(app, cors_allowed_origins="*")

HISTORY_FILE = 'chat_history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_history(messages):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False)

# 在线用户集合
online_users = set()

# 消息存储
messages = load_history()
MAX_MESSAGES = 100  # 保留最近100条消息

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if password == 'kawaimiku':
            session['username'] = username
            online_users.add(username)
            return redirect(url_for('chat'))
        else:
            error = '密码错误'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    username = session.get('username')
    if username and username in online_users:
        online_users.remove(username)
        # 广播下线消息
        socketio.emit('user_status', {
            'username': username,
            'status': 'offline',
            'time': time.strftime("%H:%M:%S")
        }, room='main_room')
        socketio.emit('update_users', list(online_users), room='main_room')
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('chat.html',
                           username=username,
                           messages=messages[-20:],
                           online_users=list(online_users))

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if not username:
        return False  # 拒绝连接
    online_users.add(username)
    join_room('main_room')
    emit('user_status', {
        'username': username,
        'status': 'online',
        'time': time.strftime("%H:%M:%S")
    }, room='main_room')
    emit('update_users', list(online_users), room='main_room')

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username and username in online_users:
        online_users.remove(username)
        emit('user_status', {
            'username': username,
            'status': 'offline',
            'time': time.strftime("%H:%M:%S")
        }, room='main_room')
        emit('update_users', list(online_users), room='main_room')

@socketio.on('send_message')
def handle_message(data):
    username = session.get('username')
    if not username:
        return
    msg = data['msg'].strip()
    if len(msg) == 0:
        return
    if len(msg) > 500:
        msg = msg[:500] + "..."
    safe_msg = escape(msg)
    message = {
        'id': str(uuid.uuid4()),
        'user': username,
        'text': safe_msg,
        'time': time.strftime("%H:%M:%S")
    }
    messages.append(message)
    if len(messages) > MAX_MESSAGES:
        messages.pop(0)
    save_history(messages)  # 新增：保存到文件
    emit('new_message', message, room='main_room')

if __name__ == '__main__':
    print("Starting chat server on http://localhost:11451")
    socketio.run(app, debug=True, host='0.0.0.0', port=11451)