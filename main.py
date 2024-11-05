from flask import Flask, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
connected_clients = {}  # Dictionary to store clients by userId


@app.route('/')
def index():
    return "WebSocket Server Running"


# WebSocket endpoint
@sock.route('/ws')
def websocket(ws):
    user_id = ws.receive()  # Receive the first message as userId
    print(connected_clients)
    if user_id:
        connected_clients[user_id] = ws
        print(f"User {user_id} connected.")

    while True:
        data = ws.receive()
        if data is None:
            break
        print(f"Received from {user_id}: {data}")

    # Remove the client on disconnect
    connected_clients.pop(user_id, None)
    print(f"User {user_id} disconnected.")


# Route to trigger message to a specific Unity client
@app.route('/trigger')
def trigger_message():
    user_id = request.args.get('userId')  # Specify the userId in the query
    message = request.args.get('message', 'clearMetalPath')

    ws = connected_clients.get(user_id)
    if ws:
        try:
            ws.send(str(message))
            return f"Message sent to user {user_id}!"
        except Exception as e:
            print(f"Error sending to user {user_id}: {e}")
            connected_clients.pop(user_id, None)
            return f"Failed to send message to user {user_id}.", 500
    else:
        return f"User {user_id} not connected.", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
