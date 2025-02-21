from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.app.database.database import PostgresDatabase
from server.app.routers.user_routers import router as user_router
from server.app.routers.admin_routers import router as admin_router
from server.app.routers.payment_routers import router as payment_router
from server.app.routers.order_routers import router as order_router
from server.app.utils.redis_client import redis_client
from server.app.services.cache_permissions_service import load_permissions


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

    yield

    redis_client.flushall()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(admin_router)
app.include_router(payment_router)

app.include_router(order_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)