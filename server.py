import asyncio
import websockets
import json

# Dictionary to store connected peers
connected_peers = {}

async def handle_connection(websocket, path):
    peer_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received message: {data}")  # Debug: log the received message

            # Handle new connection
            if data['type'] == 'new_connection':
                peer_id = data['peer_id']
                role = data['role']
                connected_peers[peer_id] = websocket
                print(f"{role.capitalize()} connected: {peer_id}")
                continue

            # Handle signaling messages (offer, answer, candidate)
            recipient_id = data.get('recipient')
            if recipient_id in connected_peers:
                await connected_peers[recipient_id].send(json.dumps(data))
                print(f"Message sent to {recipient_id}")
            else:
                print(f"Recipient {recipient_id} not found. Message discarded.")

    except websockets.ConnectionClosed:
        print(f"Connection closed: {peer_id}")
    finally:
        # Clean up when the peer disconnects
        if peer_id and peer_id in connected_peers:
            del connected_peers[peer_id]
            print(f"Peer {peer_id} removed from connected peers.")

# Start the WebSocket server
async def main():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print("WebSocket signaling server started on ws://0.0.0.0:8765")
    await server.wait_closed()

# Run the WebSocket server
asyncio.run(main())