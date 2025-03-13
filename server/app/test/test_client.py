import asyncio

import socketio
import socketio.exceptions


client = socketio.AsyncClient()


@client.event
async def user_connected(data):
    print("Connected to server")
    print(data)

@client.event
async def chat_created(data):
    chat_id = data["chat_id"]
    print(f"Created chat {chat_id}")

@client.event
async def sent_message(data):
    print(f"Received message: {data}")

@client.event
async def socketio_error(data):
    print(f"Error: {data}")


token = "<token>"


async def main():
    try:
        await client.connect(
            "ws://localhost:8000/socket.io",
            transports=["websocket"],
            headers={"Authorization": f"Bearer {token}"},
        )
    
        await asyncio.sleep(1)

        await client.emit("create_chat", {"receiver_id": 23})
        
        print(f"Requested chat creation with receiver_id = 23")
        
        await asyncio.sleep(2)
    except Exception as e:
        print("Client connection error: ", e)
    finally:
        await client.disconnect()
        
        print("Client disconnected")


if __name__ == "__main__":
    asyncio.run(main())
