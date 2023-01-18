import unittest
import json
import asyncio
import websockets
import os
import subprocess

class TestServer(unittest.TestCase):
    async def receive_with_timeout(self, websocket, timeout):
        try:
            response = json.loads(await asyncio.wait_for(websocket.recv(), timeout=timeout))
            return response
        except asyncio.TimeoutError:
            self.fail("The server did not respond within the timeout period")

    def test_join_chat(self):
        async def test_case():
            async with websockets.connect("ws://localhost:6789") as websocket:
                await websocket.send(json.dumps({"type": "register_name", "message": "test_user"}))
                response = await self.receive_with_timeout(websocket, timeout=5)
                self.assertEqual(response["type"], "join_chat")
                self.assertEqual(response["message"], "test_user has joined the chat")
        asyncio.run(test_case())

    def test_broadcast_message(self):
        async def test_case():
            async with websockets.connect("ws://localhost:6789") as websocket1:
                await websocket1.send(json.dumps({"type": "register_name", "message": "test_user1"}))
                await self.receive_with_timeout(websocket1, timeout=5)
                async with websockets.connect("ws://localhost:6789") as websocket2:
                    await websocket2.send(json.dumps({"type": "register_name", "message": "test_user2"}))
                    await self.receive_with_timeout(websocket2, timeout=5)
                    await websocket1.send(json.dumps({"type": "broadcast_message", "message": "hello"}))
                    response = await self.receive_with_timeout(websocket2, timeout=5)
                    self.assertEqual(response["type"], "broadcast_message")
                    self.assertEqual(response["message"], "test_user1: hello")
        asyncio.run(test_case())


    def test_private_message(self):
        async def test_case():
            async with websockets.connect("ws://localhost:6789") as websocket1:
                await websocket1.send(json.dumps({"type": "register_name", "message": "test_user1"}))
                await self.receive_with_timeout(websocket1, timeout=5)
                async with websockets.connect("ws://localhost:6789") as websocket2:
                    await websocket2.send(json.dumps({"type": "register_name", "message": "test_user2"}))
                    await self.receive_with_timeout(websocket2, timeout=5)
                    await websocket1.send(json.dumps({"type": "private_message", "recipient": "test_user2", "message": "hello"}))
                    response = await self.receive_with_timeout(websocket2, timeout=5)
                    self.assertEqual(response["type"], "private_message")
                    self.assertEqual(response["sender_name"], "test_user1")
                    self.assertEqual(response["message"], "hello")
                    response = await self.receive_with_timeout(websocket1, timeout=5)
                    self.assertNotEqual(response["type"], "private_message")
        asyncio.run(test_case())

    def test_online_clients_query(self):
        async def test_case():
            async with websockets.connect("ws://localhost:6789") as websocket1:
                await websocket1.send(json.dumps({"type": "register_name", "message": "test_user1"}))
                await self.receive_with_timeout(websocket1, timeout=5)
                async with websockets.connect("ws://localhost:6789") as websocket2:
                    await websocket2.send(json.dumps({"type": "register_name", "message": "test_user2"}))
                    await self.receive_with_timeout(websocket2, timeout=5)
                    await self.receive_with_timeout(websocket1, timeout=5)
                    await websocket1.send(json.dumps({"type": "online_clients_query"}))
                    response = await self.receive_with_timeout(websocket1, timeout=5)
                    self.assertEqual(response["type"], "online_clients_response")
                    self.assertIn("test_user1", response["clients"])
                    self.assertIn("test_user2", response["clients"])
        asyncio.run(test_case())

    def test_left_chat(self):
        async def test_case():
            async with websockets.connect("ws://localhost:6789") as websocket1:
                await websocket1.send(json.dumps({"type": "register_name", "message": "test_user1"}))
                await self.receive_with_timeout(websocket1, timeout=5)
                async with websockets.connect("ws://localhost:6789") as websocket2:
                    await websocket2.send(json.dumps({"type": "register_name", "message": "test_user2"}))
                    await self.receive_with_timeout(websocket2, timeout=5)
                    await websocket1.close()
                    response = await self.receive_with_timeout(websocket2, timeout=5)
                    self.assertEqual(response["type"], "left_chat")
                    self.assertEqual(response["message"], "test_user1 has left the chat")
        asyncio.run(test_case())

if __name__ == '__main__':
    asyncio.run(unittest.main())
