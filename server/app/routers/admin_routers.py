from fastapi import APIRouter, Header, HTTPException

from server.app.schemas.users_schemas import UserResponse
from server.app.utils.auth import verify_token


router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(access_tkn: str) -> bool:
    user = verify_token(access_tkn)

    return user["content"]["plan_name"] == "admin"


@router.get("/users", response_model=list[UserResponse])
async def get_users(authorization: str = Header(None)) -> list[UserResponse]:
    ...
