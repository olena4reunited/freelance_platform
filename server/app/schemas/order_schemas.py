from pydantic import BaseModel


class OrderCreate(BaseModel):
    name: str
    description: str
    images_links: list[str] | None = None


class OrderUpdate(OrderCreate):
    pass


class OrderResponse(BaseModel):
    id: int
    name: str
    description: str
    customer_id: int
    performer_id: int | None = None


class OrderListResponse(BaseModel):
    id: int
    name: str
    description: str
    customer_id: int
    performer_id: int | None = None
    image_link: str | None


class OrderSingleResponse(BaseModel):
    id: int
    name: str
    description: str
    customer_id: int
    performer_id: int | None = None
    images_links: list[str] | None


class OrderListPerformerResponse(BaseModel):
    id: int
    name: str
    description: str
    customer_id: int


class OrderPerformerAssignedResponse(OrderListPerformerResponse):
    performer_id: int