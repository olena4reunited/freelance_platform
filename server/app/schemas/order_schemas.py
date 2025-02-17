from pydantic import BaseModel


class OrderCreate(BaseModel):
    name: str
    description: str


class OrderResponse(BaseModel):
    id: int
    name: str
    description: str
    creator_id: int
    performer_id: int | None = None
