from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse

from server.app.controllers.payment_controller import PaymentController


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/add_payment", response_model=RedirectResponse)
def add_payment_details(user_id: int, payment_data: str):
    try:
        PaymentController.create_payment(user_id, payment_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Payment was not created")
    else:
        return RedirectResponse(url=f"/users/{user_id}")

