from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse

from server.app.controllers.payment_controller import PaymentController


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/add_payment", response_model=RedirectResponse)
def add_payment_details(user_id: int, payment_data: str):
    ...

