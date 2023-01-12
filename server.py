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


# from flask import Flask, render_template, request
# import json

# app = Flask(__name__)
# connected_clients = {}

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/ws')
# def handle_websocket():
#     print ("HELLLO!!!!")
#     if request.environ.get('wsgi.websocket'):
#         print ("HELLLO!!!2222222")
#         ws = request.environ['wsgi.websocket']
#         while True:
#             print ("HELLLO!!!22222223333")
#             message = json.loads(ws.receive())
#             if message["type"] == "register_name":
#                 name = message["message"]
#                 connected_clients[name] = ws
#                 emit_message_to_all({'message': f'{name} has joined the chat'}, 'join_leave')
#             elif message["type"] == "private_message":
#                 recipient = message["recipient"]
#                 message = message["message"]
#                 emit_message_to_client({'message': message}, connected_clients[recipient], 'private_message')
#             elif message["type"] == "online_clients_query":
#                 online_clients = list(connected_clients.keys())
#                 emit_message_to_client({'clients': online_clients}, ws, 'online_clients_response')
#             else:
#                 emit_message_to_all({'message': message["message"]}, 'broadcasted_message')
#     return ''

# def emit_message_to_all(message, event_name):
#     for client in connected_clients.values():
#         client.send(json.dumps({'event': event_name, 'message': message}))

# def emit_message_to_client(message, client, event_name):
#     client.send(json.dumps({'event': event_name, 'message': message}))

# if __name__ == '__main__':
#     app.run()


# @socketio.on('message')
# def handle_client_message(message):
#     print(message)
#     print('<<<<<<<<<')
#     message = json.loads(message)
#     if message["type"] == "register_name":
#         name = message["message"]
#         connected_clients[name] = request.sid
#         emit('join_leave', {'message': f'{name} has joined the chat'}, broadcast=True)
#     elif message["type"] == "private_message":
#         recipient = message["recipient"]
#         message = message["message"]
#         emit('private_message', {'message': message}, room=connected_clients[recipient])
#     elif message["type"] == "online_clients_query":
#         online_clients = list(connected_clients.keys())
#         emit('online_clients_response', {'clients': online_clients}, room=request.sid)
#     else:
#         emit('broadcasted_message', {'message': message["message"]}, broadcast=True)


    # <!-- <script>
    #   var ws = new WebSocket('ws://' + window.location.host + '/ws');

    #   let name = "";
    #   ws.onopen = () => {
    #     name = prompt("What's your name?");
    #     const registerMessage = { type: "register_name", message: name };
    #     ws.send(JSON.stringify(registerMessage));
    #   };

    #   ws.onmessage = event => {
    #     // Handle messages received from the server
    #     const message = JSON.parse(event.data);
    #     if(message.type === 'online_clients_response'){
    #         updateOnlineClientsUI(message.clients);
    #     }else{
    #       var msg = document.createElement("p");
    #       var text = document.createTextNode(message.message);
    #       msg.appendChild(text);
    #       document.getElementById("messages").appendChild(msg);
    #     }
    #   };

    #   ws.onclose = () => {
    #     // Handle connection close
    #     console.log("Connection closed");
    #   };

    #   function requestOnlineClients(){
    #     const onlineClientsQuery = { type: "online_clients_query" };
    #     ws.send(JSON.stringify(onlineClientsQuery));
    # }

    #   // Send a private message to a specific user
    #   function sendPrivateMessage() {
    #     var recipient = document.getElementById("recipient").value;
    #     var message = document.getElementById("message").value;
    #     const privateMessage = { type: "private_message", recipient: recipient, message: message };
    #     ws.send(JSON.stringify(privateMessage));
    #   }

    #   function sendMessage() {
    #     var recipient = document.getElementById("recipient").value;
    #     var message = document.getElementById("message").value;
    #     if (recipient) {
    #         sendPrivateMessage();
    #     } else {
    #       const normalMessage = { type: "normal_message", message: message };
    #       ws.send(JSON.stringify(normalMessage));
    #     }
    #     document.getElementById("message").value = "";
    #     document.getElementById("recipient").value = "";
    #   }


    # function updateOnlineClientsUI(clients) {
    #     let onlineClientsList = document.getElementById("online-clients-list");
    #     onlineClientsList.innerHTML = "";
    #     for (const client of clients) {
    #         let clientItem = document.createElement("li");
    #         let text = document.createTextNode(client);
    #         clientItem.appendChild(text);
    #         onlineClientsList.appendChild(clientItem);
    #     }
    # }
    # </script> -->