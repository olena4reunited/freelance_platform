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
    print(auth)
    print(environ)
    print(sid)
    headers = dict(environ["asgi.scope"]["headers"])
    auth_headers = next((v for k, v in headers.items() if k == "Authorization"), None)

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
    receiver_id = data["receiver_id"]

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
                return

            cursor.execute(
                """
                    SELECT id
                    FROM orders
                    WHERE customer_id = %s AND performer_id = %s
                """,
                (customer_id, performer_id)
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
                return

            cursor.execute(
                """
                    SELECT id
                    FROM chats
                    WHERE customer_id = %s AND performer_id = %s
                """,
                (customer_id, performer_id)
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
                return

            cursor.execute(
                """
                    INSERT INTO chats (customer_id, performer_id, messages)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """,
                (customer_id, performer_id, "[]")
            )
            chat_row = cursor.fetchone()
        
        chat_id = chat_row[0] if chat_row else -1

        if chat_id == -1:
            await sio.emit(
                "error",
                {
                    "status_code": 400,
                    "detail": "Chat creation failed",
                },
                to=sid,
            )
            return
        
        await sio.enter_room(sid, room=f"chat_{chat_id}")
        await sio.emit("chat_created", {"chat_id": chat_id}, room=f"chat_{chat_id}")


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
    chat_id = data["chat_id"]
    session = await sio.get_session(sid)
    user = session["user"]
    content = data["content"]

    message = {
        "sender_id": user["id"],
        "content": content,
        "created_at": datetime.now().isoformat()
    }

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE chats
                    SET messages = messages || %s::jsonb
                    WHERE id = %s
                """,
                (json.dumps([message], indent=2), chat_id)
            )

    await sio.emit("receive_message", message, room=f"chat_{chat_id}")


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    user = session.get("user") if session else None

    if not user:
        return

    user_id = user.get("id")

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM chats 
                WHERE customer_id = %s OR performer_id = %s
                """,
                (user_id, user_id)
            )
            chat_ids = [row[0] for row in cursor.fetchall()]
    
    for chat_id in chat_ids:
        await sio.emit(
            "user_disconnected",
            {"user_id": user_id, "message": "User left the chat"},
            room=f"chat_{chat_id}"
        )
        await sio.leave_room(sid, room=f"chat_{chat_id}")
