import asyncio

import socketio
import socketio.exceptions


client = socketio.AsyncClient()


async def main():
    await client.connect(
        "ws://localhost:8000",
        transports=["websocket"],
        headers={"Authorization": "<token>"},
        socketio_path="/ws"
    )
    print("Client connected")
    print("Client sid is: ", client.sid)
    print("Client transport is: ", client.transport)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
