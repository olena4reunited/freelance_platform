import asyncio
import json
from datetime import datetime

import socketio

from server.app.database.database import PostgresDatabase
from server.app.controllers.user_controller import UserController
from server.app.utils.auth import verify_token


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["*"],
    logger=True,
    engineio_logger=True
)


@sio.event
async def connect(sid, environ, auth):
    try:
        headers = {k.decode("utf-8"): v for k, v in environ["asgi.scope"]["headers"]}
        auth_headers = headers.get("authorization")
    except Exception as e:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": str(e),
            },
            to=sid,
        )
        return False

    if not auth_headers:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Authorization header is missing",
            },
            to=sid,
        )
        return False

    try:
        token = auth_headers.decode("utf-8").split(" ")[1]
        verify_token(token)
        user = UserController.get_user_by_token(token)
    except Exception as e:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": str(e),
            },
            to=sid,
        ) 
        return False

    await sio.save_session(sid, {"user": user})
    return True


@sio.event
async def create_chat(sid, data):
    session = await sio.get_session(sid)

    if not session:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        return

    sender = session.get("user")
    receiver_id = data["receiver_id"]

    if not receiver_id:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Receiver id is missing",
            }
        )
        return

    with PostgresDatabase(on_commit=True) as db:
        with db.connection.cursor() as cursor:
            sender_id = sender.get("id")
            sender_plan = sender.get("plan_name")

            cursor.execute(
                """
                    SELECT id
                    FROM chats
                    WHERE (user_one_id = %s AND user_two_id = %s)
                        OR (user_one_id = %s AND user_two_id = %s)
                """,
                (sender_id, receiver_id, receiver_id, sender_id)
            )
            chat_id = cursor.fetchone()[0] if cursor.fetchone() else None
            
            if chat_id:
                await sio.emit(
                    "info",
                    {
                        "status": "error",
                        "detail": "Chat with selected user already exists",
                    },
                    to=sid,
                )
                await sio.enter_room(sid, room=f"chat_{chat_id}")

            if sender_plan in ["customer", "performer"]:
                cursor.execute(
                    """
                        SELECT id
                        FROM orders
                        WHERE (customer_id = %s AND performer_id = %s) 
                            OR (customer_id = %s AND performer_id = %s) 
                    """,
                    (sender_id, receiver_id, receiver_id, sender_id)
                )
                if not cursor.fetchone():
                    await sio.emit(
                        "info",
                        {
                            "status": "error",
                            "detail": "You and selected user aren't joined by order",
                        },
                        to=sid,
                    )
                    return

            cursor.execute(
                """
                    INSERT INTO chats (user_one_id, user_two_id, messages)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """,
                (sender_id, receiver_id, "[]")
            )
            chat_row = cursor.fetchone()
        
        chat_id = chat_row[0] if chat_row else -1

        if chat_id == -1:
            await sio.emit(
                "info",
                {
                    "status": "error",
                    "detail": "Chat creation failed",
                },
                to=sid,
            )
            return
        
        await sio.enter_room(sid, room=f"chat_{chat_id}")
        await sio.emit("chat_created", {"chat_id": chat_id}, room=f"chat_{chat_id}")


@sio.event
async def join_chat(sid, data):
    session = await sio.get_session(sid)

    if not session:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        return

    user = session.get("user")
    user_id = user.get("id")    

    chat_id = data.get("chat_id")

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT 1
                    FROM chats
                    WHERE id = %s AND (user_one_id = %s OR user_two_id = %s)
                """,
                (chat_id, user_id, user_id)
            )
            
            if not cursor.fetchone():
                await sio.emit(
                    "info",
                    {
                        "status": "error",
                        "detail": "Chat not found or user is not a member",
                    },
                    to=sid,
                )
                return

            cursor.execute(
                """
                    SELECT messages
                    FROM chats
                    WHERE id = %s
                """,
                (chat_id, )
            )
            chat = cursor.fetchone()

    await sio.enter_room(sid, room=f"chat_{chat_id}")

    messages = chat[0] if chat else []

    await sio.emit("chat_history", {"messages": messages}, to=sid)


@sio.event
async def send_message(sid, data):
    session = await sio.get_session(sid)

    if not session:
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        return

    user = session["user"]
    user_id = user.get("id")
    chat_id = data.get("chat_id")
    content = data.get("content")

    message = {
        "sender_id": user_id,
        "content": content,
        "created_at": datetime.now().isoformat()
    }

    with PostgresDatabase(on_commit=True) as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT 1
                    FROM chats
                    WHERE id = %s AND (user_one_id = %s OR user_two_id = %s)
                """,
                (chat_id, user_id, user_id)
            )
            
            if not cursor.fetchone():
                await sio.emit(
                    "info",
                    {
                        "status": "error",
                        "detail": "Chat not found or user is not a member",
                    },
                    to=sid,
                )
                return
    
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
        await sio.emit(
            "info",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        return

    user_id = user.get("id")

    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM chats 
                WHERE user_one_id = %s OR user_two_id = %s
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
