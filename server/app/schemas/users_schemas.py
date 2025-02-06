from pydantic import BaseModel, EmailStr, constr, condecimal, conint

from server.app.schemas.plans_schemas import PlanEnum


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone_number: str
    password: str
    password_repeat: str
    plan_id: PlanEnum



class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: constr(min_length=10, max_length=13) | None = None
    password: str
    photo_link: str | None = None
    description: str | None = None
    is_verified: bool = False
    balance: condecimal(max_digits=10, decimal_places=2) = None
    rating: conint(ge=0, le=5) = None
    plan_id: PlanBase

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int

