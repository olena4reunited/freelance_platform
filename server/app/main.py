from contextlib import asynccontextmanager
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
import socketio

from server.app.services.chat_service import sio
from server.app.database.database import PostgresDatabase
from server.app.routers.user_routers import router as user_router
from server.app.routers.admin_routers import router as admin_router
from server.app.routers.payment_routers import router as payment_router
from server.app.routers.order_routers import router as order_router
from server.app.routers.profile_routers import router as profile_router
from server.app.utils.redis_client import redis_client
from server.app.services.cache_permissions_service import load_permissions
from server.app.utils.exceptions import (
    GlobalException,
    global_exception_handler,
    response_validation_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_permissions()
    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE orders
                    SET is_blocked = FALSE, blocked_until = NULL
                    WHERE CURRENT_DATE > blocked_until AND is_blocked = TRUE;
                """
            )
            cursor.execute(
                """
                    UPDATE users
                    SET is_blocked = FALSE, block_expired = NULL
                    WHERE CURRENT_DATE > block_expired and is_blocked = TRUE;
                """
            )

    try:
        yield
    except asyncio.CancelledError:
        pass

    redis_client.flushall()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(GlobalException, global_exception_handler)
app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)

app.mount("/socket.io", socketio.ASGIApp(sio))

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(payment_router)
app.include_router(order_router)
app.include_router(profile_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=True)
