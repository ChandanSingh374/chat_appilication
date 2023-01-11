import json
import asyncio
import websockets

connected_clients = {}

async def broadcast(message, type):
    """
    This function broadcast the received message to all the connected clients
    """
    message = {"type": type, "message": message}
    message = json.dumps(message)
    for name in connected_clients:
        await connected_clients[name].send(message)

async def send_custom_response(name, message):
    """
    This function sends a custom message to the specific client
    """
    for client in connected_clients:
        if name == client:
            message = {"type": "private_message", "message": message}
            message = json.dumps(message)
            await connected_clients[name].send(message)

async def handle_client(client, path):
    """
    This function handles the connected client, receives messages, and broadcast to all or sends custom message to specific client
    """
    try:
        while True:
            message = json.loads(await client.recv())
            if message["type"] == "register_name":
                name = message["message"]
                connected_clients[name] = client
                await broadcast(f'{name} has joined the chat', "join_leave")
                
            elif message["type"] == "private_message":
                recipient = message["recipient"]
                message = message["message"]
                await send_custom_response(recipient, f'{name}: {message}')
                
            elif message["type"] == "online_clients_query":
                online_clients = list(connected_clients.keys())
                await client.send(json.dumps({"type": "online_clients_response", "clients": online_clients}))
            else:
                await broadcast(f'{name}: {message["message"]}', "broadcasted_message")
    finally:
        del connected_clients[name]
        await broadcast(f'{name} has left the chat', "join_leave")

def main():
    start_server = websockets.serve(handle_client, "localhost", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
