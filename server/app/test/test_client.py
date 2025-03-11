import asyncio

import socketio
import socketio.exceptions


client = socketio.AsyncClient()


@client.event
async def chat_created(data):
    chat_id = data["chat_id"]

    print(f"Chat created: {chat_id}")

    await client.emit("send_message", {"chat_id": chat_id, "content": "Hello, world!"})

    print(f"Sent message to chat {chat_id}")

@client.event
async def receive_message(data):
    print(f"Received message: {data}")

@client.event
async def error(data):
    print(f"Error: {data}")


token = "<token>"


async def main():
    try:
        await client.connect(
            "ws://localhost:8000/socket.io",
            transports=["websocket"],
            headers={"Authorization": f"Bearer {token}"},
        )

        print("Client connected")
        print("Client sid is: ", client.sid)
        print("Client transport is: ", client.transport)
    
        await asyncio.sleep(1)

        await client.emit("create_chat", {"receiver_id": 23})
        
        print(f"Requested chat creation with receiver_id = 23")
        
        await asyncio.sleep(5)
    except Exception as e:
        print("Client connection error: ", e)
    finally:
        await client.disconnect()
        
        print("Client disconnected")


if __name__ == "__main__":
    asyncio.run(main())
