from pydantic import BaseModel


class PermissionCreate(BaseModel):
    permission: str
    plans: list[str] | str | None = None


class PermissionResponse(BaseModel):
    plan: str
    permission: str
