from pydantic import BaseModel


class PermissionCreate(BaseModel):
    permission: str
    plans: list[str] | str | None = None


class PermissionUpdate(BaseModel):
    permission: str | None = None
    plans: list[str] | str | None = None


class PermissionResponse(BaseModel):
    permission: str
    plan: str
