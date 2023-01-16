import json
import asyncio
import websockets

async def register_name(name):
    await ws.send(json.dumps({"type": "register_name", "message": name}))
    response = json.loads(await ws.recv())
    print(response["message"])

async def send_message(message):
    await ws.send(json.dumps({"type": "broadcasted_message", "message": message}))

async def send_private_message(recipient, message):
    await ws.send(json.dumps({"type": "private_message", "recipient": recipient, "message": message}))

async def query_online_clients():
    await ws.send(json.dumps({"type": "online_clients_query"}))
    response = json.loads(await ws.recv())
    print("Online clients:", response["clients"])

async def main():
    global ws
    ws = await websockets.connect('ws://localhost:6789')
    name = input("Enter your name:")
    await register_name(name)
    while True:
        message = input()
        if message.startswith("@"):
            recipient, message = message.split(" ", 1)
            recipient = recipient[1:]
            await send_private_message(recipient, message)
        elif message == "?online":
            await query_online_clients()
        else:
            await send_message(message)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
