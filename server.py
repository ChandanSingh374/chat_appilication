import json
import asyncio
import websockets

class ChatServer:
    def __init__(self):
        self.connected_clients = {}

    async def broadcast(self, message, message_type):
        """
        This function broadcast the received message to all the connected clients
        """
        message = {"type": message_type, "message": message}
        message = json.dumps(message)
        for name in self.connected_clients:
            await self.connected_clients[name].send(message)

    async def send_custom_response(self, recipant_name, sender_name, message):
        """
        This function sends a custom message to the specific client
        """
        for client in self.connected_clients:
            if recipant_name == client:
                message = {"type": "private_message", "message": message, "sender_name": sender_name}
                message = json.dumps(message)
                await self.connected_clients[recipant_name].send(message)

    async def handle_client(self, client, path):
        """
        This function handles the connected client, receives messages, and broadcast to all or sends custom message to specific client
        """
        try:
            while True:
                message = json.loads(await client.recv())
                if message["type"] == "register_name":
                    name = message["message"]
                    self.connected_clients[name] = client
                    await self.broadcast(f'{name} has joined the chat', "join_chat")

                elif message["type"] == "private_message":
                    recipient = message["recipient"]
                    message = message["message"]
                    await self.send_custom_response(recipient, name, message)

                elif message["type"] == "online_clients_query":
                    online_clients = list(self.connected_clients.keys())
                    await client.send(json.dumps({"type": "online_clients_response", "clients": online_clients}))
                else:
                    await self.broadcast(f'{name}: {message["message"]}', "broadcast_message")
        finally:
            del self.connected_clients[name]
            await self.broadcast(f'{name} has left the chat', "left_chat")

    def run(self):
        start_server = websockets.serve(self.handle_client, "localhost", 6789)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run()
