import asyncio
import json
from datetime import datetime

import socketio

from server.app.utils.dependencies.dependencies import get_current_user
from server.app.database.database import PostgresDatabase
from server.app.utils.exceptions import GlobalException


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["*"],
    logger=True,
    engineio_logger=True
)


@sio.event
async def connect(sid, environ, auth):
    headers = environ["asgi.scope"]["headers"]
    auth_headers = next((h for h in headers if h[0] == b"Authorization"), None)

    if not auth_headers:
        return False

    token = auth_headers[1].decode("utf-8").split(" ")[1]
    user = await get_current_user(token)

    await sio.save_session(sid, {"user": user})
    return True


@sio.event
async def create_chat(sid, data):
    session = await sio.get_session(sid)
    sender = session.get("user")
    receiver_id = data.get("receiver_id")

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    WITH selected_user_plan AS (
                        SELECT plan_id
                        FROM users
                        WHERE id = %s
                    )
                    SELECT pln.name AS name
                    FROM plans pln
                    JOIN selected_user_plan sup
                        ON sup.plan_id = pln.id
                """,
                (receiver_id,)
            )
            receiver_plan = cursor.fetchone()[0]

            if (sender.get("plan_name"), receiver_plan) == ("customer", "performer"):
                customer_id, performer_id = sender.get("id"), receiver_id
            elif (sender.get("plan_name"), receiver_plan) == ("performer", "customer"):
                customer_id, performer_id = receiver_id, sender.get("id")
            else:
                await sio.emit(
                    "error",
                    {
                        "status_code": 403,
                        "detail": "You cannot start a chat with selected user",
                    },
                    to=sid,
                )

            cursor.execute(
                """
                    SELECT id
                    FROM orders
                    WHERE customer_id = %s AND performer_id = %s
                """
            )
            if not cursor.fetchone():
                await sio.emit(
                    "error",
                    {
                        "status_code": 403,
                        "detail": "You and selected user aren't joined by the order",
                    },
                    to=sid,
                )

            cursor.execute(
                """
                    SELECT id
                    FROM chats
                    WHERE customer_id = %s AND performer_id = %s
                """
            )
            if cursor.fetchone():
                await sio.emit(
                    "error",
                    {
                        "status_code": 400,
                        "detail": "Chat with selected user already exists",
                    },
                    to=sid,
                )

            cursor.execute(
                """
                    INSERT INTO chats (customer_id, performer_id, messages)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """,
                (customer_id, performer_id, "[]")
            )
            chat_id = cursor.fetchone().get("id")

        await sio.emit("chat_created", {"chat_id": chat_id}, to=sid)


@sio.event
async def join_chat(sid, data):
    chat_id = data.get("chat_id")
    await sio.enter_room(sid, room=f"chat_{chat_id}")

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT messages
                    FROM chats
                    WHERE id = %s
                """,
                (chat_id, )
            )
            chat = cursor.fetchone()

            if chat:
                messages = chat[0]
                await sio.emit("chat_history", {"messages": messages}, to=sid)


@sio.event
async def send_message(sid, data):
    chat_id = data.get("chat_id")
    session = await sio.get_session(sid)
    user = session.get("user")
    content = data.get("content")

    message = {
        "sender_id": user.get("id"),
        "content": content,
        "created_at": datetime.now()
    }

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE chats
                    SET messages = messages || %s::jsonb
                    WHERE id = %s
                """,
                (json.dumps(message, indent=2), chat_id)
            )
