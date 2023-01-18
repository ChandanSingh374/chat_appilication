import json
import asyncio
import websockets
import socket

connected_clients = {}

async def broadcast(message, message_type):
    """
    This function broadcast the received message to all the connected clients
    """
    message = {"type": message_type, "message": message}
    message = json.dumps(message)
    for name in connected_clients:
        await connected_clients[name].sendall(message.encode())

async def send_custom_response(recipant_name, sender_name, message):
    """
    This function sends a custom message to the specific client
    """
    for client in connected_clients:
        if recipant_name == client:
            message = {"type": "private_message", "message": message, "sender_name": sender_name}
            message = json.dumps(message)
            await connected_clients[recipant_name].sendall(message.encode())

async def handle_client(client_socket):
    try:
        name = ""
        while True:
            message = json.loads(await client_socket.recv(1024).decode())
            if message["type"] == "register_name":
                name = message["message"]
                connected_clients[name] = client_socket
                await broadcast(f'{name} has joined the chat', "join_chat")
                
            elif message["type"] == "private_message":
                recipient = message["recipient"]
                message = message["message"]
                await send_custom_response(recipient, name, message)
                
            elif message["type"] == "online_clients_query":
                online_clients = list(connected_clients.keys())
                await client_socket.sendall(json.dumps({"type": "online_clients_response", "clients": online_clients}).encode())
            else:
                await broadcast(f'{name}: {message["message"]}', "broadcast_message")
    finally:
        del connected_clients[name]
        await broadcast(f'{name} has left the chat', "left_chat")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6789))
    server_socket.listen()
    
    while True:
        client_socket, address = server_socket.accept()
        asyncio.get_event_loop().run_until_complete(handle_client(client_socket))

if __name__ == '__main__':
    main()
