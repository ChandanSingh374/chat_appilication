from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request
import json

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", async_handlers=True, pingTimeout=900)

connected_clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_client_connect():
    print('Client connected')

@socketio.on('register_name')
def handle_update_name(message):
    connected_clients[request.sid] = {}
    name = message["message"]
    connected_clients[request.sid]["name"] = name
    emit('join_leave', {'message': f'{name} has joined the chat'}, broadcast=True)

@socketio.on('private_message')
def handle_private_message(message):
    recipient = message["recipient"]
    message = message["message"]
    recipient_session = session_via_name(recipient)
    if recipient_session:
        emit('private_message', {'message': message, 'sender': current_user_name()}, room=recipient_session)

@socketio.on('broadcast_message')
def handle_broadcast_message(message):
    message = message["message"]
    response = {'message': message, 'sender': current_user_name()}
    print(response)
    emit('broadcast_message', response, broadcast=True)

@socketio.on('online_clients_list')
def online_clients_list(message):
    online_clients = list(connected_clients.values())
    print(online_clients)
    emit('online_clients_list', {'clients': online_clients}, room=request.sid)

def current_user_name():
    return connected_clients[request.sid]["name"]

def session_via_name(name):
    for key in connected_clients:
        if connected_clients[key]["name"] == name:
            return key

@socketio.on('disconnect')
def handle_client_disconnect():
    name = connected_clients[request.sid]["name"]
    del connected_clients[request.sid]
    emit('join_leave', {'message': f'{name} has left the chat'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
