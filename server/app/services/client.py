import asyncio

import socketio


client = socketio.AsyncClient()


async def main():
    await client.connect("http://localhost:8000", transports=["websocket"])
    print("Client connected")
    print("Client sid is: ", client.sid)
    print("Client transport is: ", client.transport)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
