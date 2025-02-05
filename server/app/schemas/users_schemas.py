from pydantic import BaseModel, EmailStr, constr, condecimal, conint

from server.app.schemas.plans_schemas import PlanBase


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: constr(min_length=10, max_length=13)
    password: constr(min_length=8)
    photo_link: str | None = None
    description: str | None = None
    is_verified: bool = False
    balance: condecimal(max_digits=10, decimal_places=2)
    rating: conint(ge=0, le=5)
    plan_id: PlanBase

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int

