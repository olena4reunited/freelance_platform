from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: str | None = None
    password: str
    password_repeat: str


class UserCreateCustomer(UserCreate):
    payment: str


class UserCreatePerformer(UserCreate):
    specialities: list[int] | None = None


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
    specialities: list[int] | None = None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: str | None
    photo_link: str | None
    description: str | None
    balance: Annotated[Decimal, Field(strict=True, max_digits=10, decimal_places=2)] | None
    rating: Annotated[int, Field(strict=True, ge=0, le=5)] | None
    plan_name: str


class UserResponsePerformer(UserResponse):
    specialities: list[str] | None


class UserResponseExtended(UserResponse):
    is_verified: bool | None
    block_expired: datetime | None
    delete_date: datetime | None
    is_blocked: bool | None


class UserResponseExtendedPerformer(UserResponseExtended):
    specialities: list[int] | list[str] | None


class UserCreateToken(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str


class UserPerformerResponse(BaseModel):
    order_ids: list[int]
    username: str
    first_name: str
    last_name: str
    photo_link: str | None


class UserCustomerResponse(UserPerformerResponse):
    pass


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirmRequest(BaseModel):
    email: str
    code: str
    password: str
    password_repeat: str
