import json
from datetime import datetime
from functools import wraps
import traceback

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


def handle_socketio_errors(func):
    @wraps(func)
    async def wrapper(sid, *args, **kwargs):
        try:
            await func(sid, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            await sio.emit(
                "socketio_error",
                {
                    "status": "error",
                    "detail": str(e),
                },
                to=sid
            )
            await sio.disconnect(sid)
            return
    return wrapper


@sio.event
@handle_socketio_errors
async def connect(sid, environ,  *args, **kwargs):
    headers = {k.decode("utf-8"): v for k, v in environ["asgi.scope"]["headers"]}
    auth_headers = headers.get("authorization")

    if not auth_headers:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Authorization header is missing",
            },
            to=sid,
        )
        await sio.disconnect(sid)
        return

    token = auth_headers.decode("utf-8").split(" ")[1]
    verify_token(token)
    user = UserController.get_user_by_token(token)
    
    await sio.emit(
        "user_connected",
        {"user_id": user.get("id"), "message": "User connected"},
        to=sid
    )
    await sio.save_session(sid, {"user": user})


@sio.event
@handle_socketio_errors
async def create_chat(sid, data,  *args, **kwargs):
    session = await sio.get_session(sid)
    
    if not session:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        await sio.disconnect(sid)
        return

    sender = session.get("user")
    receiver_id = data["receiver_id"]
    
    if not receiver_id:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Receiver id is missing",
            }
        )
        await sio.disconnect(sid)
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
            chat_id = cursor.fetchone()

            if chat_id:
                await sio.enter_room(sid, room=f"chat_{chat_id}")
                await sio.emit(
                    "socketio_error",
                    {
                        "status": "error",
                        "detail": "Chat with selected user already exists",
                    },
                    to=sid,
                )
                return

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
                        "socketio_error",
                        {
                            "status": "error",
                            "detail": "You and selected user aren't joined by order",
                        },
                        to=sid,
                    )
                    await sio.disconnect(sid)
                    return

            cursor.execute(
                """
                    INSERT INTO chats (user_one_id, user_two_id, messages)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """,
                (sender_id, receiver_id, "[]")
            )
            chat_id = cursor.fetchone()[0]
        
        if not chat_id:
            await sio.emit(
                "socketio_error",
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
@handle_socketio_errors
async def join_chat(sid, data,  *args, **kwargs):
    session = await sio.get_session(sid)

    if not session:
        await sio.emit(
            "socketio_error",
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
                    "socketio_error",
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
@handle_socketio_errors
async def send_message(sid, data,  *args, **kwargs):
    session = await sio.get_session(sid)

    if not session:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Session is not found",
            },
            to=sid,
        )
        return

    user_id = session.get("user").get("id")
    chat_id = data.get("chat_id")
    content = data.get("content")

    if not chat_id:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Chat id is missing",
            },
            to=sid,
        )
        return
    if content == None:
        await sio.emit(
            "socketio_error",
            {
                "status": "error",
                "detail": "Message content is missing",
            },
            to=sid,
        )
        return

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
                    "socketio_error",
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

    await sio.emit("sent_message", message, room=f"chat_{chat_id}")


@sio.event
@handle_socketio_errors
async def disconnect(sid, *args, **kwargs):
    session = await sio.get_session(sid)
    user = session.get("user")

    if not user:
        await sio.emit(
            "socketio_error",
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
