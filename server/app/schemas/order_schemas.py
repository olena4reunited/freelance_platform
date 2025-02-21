from datetime import datetime

from pydantic import BaseModel


class OrderCreate(BaseModel):
    name: str
    description: str
    images_links: list[str] | None = None


class OrderUpdate(OrderCreate):
    name: str | None = None
    description: str | None = None
    images_links: list[str] | None = None


class OrderListResponse(BaseModel):
    id: int
    name: str
    description: str | None
    customer_id: int
    performer_id: int | None = None
    image_link: str | None


class OrderSingleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    customer_id: int
    performer_id: int | None = None
    images_links: list[str] | None = None


class OrderSingleResponseExtended(OrderSingleResponse):
    blocked_until: datetime
    is_blocked: bool


class OrderListPerformerResponse(BaseModel):
    id: int
    name: str
    description: str
    customer_id: int


class OrderPerformerAssignedResponse(OrderListPerformerResponse):
    performer_id: int


class OrderAdminUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    customer_id: int | None = None
    performer_id: int | None = None
    images_links: list[str] | None = None
