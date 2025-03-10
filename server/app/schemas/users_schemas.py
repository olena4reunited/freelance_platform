from datetime import datetime

from pydantic import BaseModel, condecimal, conint


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: str
    password: str
    password_repeat: str


class UserCreateCustomer(UserCreate):
    payment: str


class UserCreatePerformer(UserCreate):
    pass


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    phone_number: str | None = None
    password: str | None = None
    password_repeat: str | None = None
    photo_link: str | None = None
    description: str | None = None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: str
    photo_link: str | None
    description: str | None
    balance: Annotated[Decimal, Field(strict=True, max_digits=10, decimal_places=2)] | None
    rating: Annotated[int, Field(strict=True, ge=0, le=5)] | None
    plan_name: str


class UserResponseExtended(UserResponse):
    is_verified: bool
    block_expired: datetime
    delete_date: datetime | None
    is_blocked: bool


class UserCreateToken(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str


class UserPerformerResponse(BaseModel):
    id: int
    order_ids: list[int]
    username: str
    first_name: str
    last_name: str
    photo_link: str | None


class UserCustomerResponse(UserPerformerResponse):
    pass
