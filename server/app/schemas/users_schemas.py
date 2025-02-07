from typing import Literal

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
    first_name: str | None
    last_name: str | None
    username: str | None
    email: str | None
    phone_number: str | None
    password: str | None
    password_repeat: str | None
    photo_link: str | None
    description: str | None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: str
    photo_link: str | None
    description: str | None
    balance: condecimal(max_digits=10, decimal_places=2) | None
    rating: conint(ge=0, le=5) | None
    plan_name: str
