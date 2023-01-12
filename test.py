import unittest
from flask import Flask
from flask_socketio import SocketIO

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
    emit('broadcast_message', response, broadcast=True)

@socketio.on('online_clients_list')
def online_clients_list(message):
    online_clients = list(connected_clients.values())
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


class TestFlaskSocketIO(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.socketio = socketio
        self.client = self.socketio.test_client(self.app)
        global connected_clients
        connected_clients = {}

    def test_client_connect(self):
        # Test that a client can connect to the server
        self.client.emit('connect')

    def test_register_name(self):
        # Test that a client can register their name with the server
        name = 'Test User'
        self.client.emit('register_name', {'message': name})
        received = self.client.get_received()
        self.assertTrue(len(received) > 0)
        self.assertEqual(received[0]['args'][0]['message'], f'{name} has joined the chat')
        
    def test_private_message(self):
        # Test that a client can send a private message to another client
        self.client.emit('register_name', {'message': 'Test User'})
        self.client.emit('private_message', {'recipient': 'Test User', 'message': 'Hello, how are you?'})
        received = self.client.get_received()
        self.assertTrue(len(received) > 0)
        received_length = len(received)
        self.assertEqual(received[received_length-1]['args'][0]['message'], 'Hello, how are you?')
        self.assertEqual(received[received_length-1]['args'][0]['sender'], 'Test User')
        
    def test_broadcast_message(self):
        # Test that a client can send a broadcast message to all clients
        self.client.emit('register_name', {'message': 'Test User'})
        self.client.emit('broadcast_message', {'message': 'Hello, everyone!'})
        received = self.client.get_received()
        received_length = len(received)
        self.assertTrue(len(received) > 0)
        self.assertEqual(received[received_length-1]['args'][0]['message'], 'Hello, everyone!')
        self.assertEqual(received[received_length-1]['args'][0]['sender'], 'Test User')
        
    def test_online_clients_list(self):
        # Test that a client can receive a list of online clients
        self.client.emit('register_name', {'message': 'Test User'})
        self.client.emit('online_clients_list', {})
        received = self.client.get_received()
        received_length = len(received)
        self.assertTrue(len(received) > 0)
        self.assertEqual(received[received_length-1]['args'][0]['clients'], [{'name': 'Test User'}])

if __name__ == '__main__':
    unittest.main()
