from datetime import datetime

from pydantic import BaseModel, Field


class PerformerBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    photo_link: str | None


class TeamBase(BaseModel):
    name: str
    lead: PerformerBase | None = None
    performers: list[PerformerBase] | PerformerBase


class OrderCreate(BaseModel):
    name: str
    description: str
    execution_type: str = Field(pattern=r"^(single|team)$")
    images_links: list[str] | None = None
    tags: list[str]


class OrderUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    images_links: list[str] | None = None
    tags: list[str] | None = None


class OrderListResponse(BaseModel):
    id: int
    name: str
    description: str | None
    customer_id: int
    execution_type: str
    performer_id: int | None
    performer_team_id: int | None
    image_link: str | None
    tags: list[str]


class OrderDetailResponseBase(BaseModel):
    id: int
    name: str
    description: str | None
    customer_id: int
    execution_type: str
    images_links: list[str] | None
    tags: list[str]


class OrderDetailResponseSingle(OrderDetailResponseBase):
    performer: PerformerBase


class OrderDetailResponseTeam(OrderDetailResponseBase):
    team: TeamBase


class OrderSingleResponseExtended(OrderDetailResponseBase):
    blocked_until: datetime
    is_blocked: bool


class OrderAdminUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    customer_id: int | None = None
    performer_id: int | None = None
    images_links: list[str] | None = None
