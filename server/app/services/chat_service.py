import asyncio

import socketio


sio_server = socketio.AsyncServer(
    client_manager=socketio.AsyncManager(),
    async_mode="asgi",
    cors_allowed_origins=["*"],
    logger=True,
    engineio_logger=True
)
sio = socketio.ASGIApp(socketio_server=sio_server)

sio_client = socketio.AsyncClient()


@sio_server.event
async def connect(sid, environ, auth):
    print(f"{sid}: connected")
