from pydantic import BaseModel


class PaymentCreate(BaseModel):
    payment: str


class PaymentResponse(BaseModel):
    id: int
    payment: str


class PaymentResponseExtended(BaseModel):
    id: int
    user_id: int
    payment: str
