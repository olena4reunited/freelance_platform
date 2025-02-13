import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.app.routers.user_routers import router as user_router
from server.app.routers.admin_routers import router as admin_router
from server.app.routers.payment_routers import router as payment_router


app = FastAPI()

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


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)