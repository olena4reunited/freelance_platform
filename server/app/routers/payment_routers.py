from typing import Any, Union

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from server.app.validators.payment_validators import PaymentValidator
from server.app.controllers.payment_controller import PaymentController
from server.app.utils.dependencies import (
    required_permissions,
    required_plans,
    get_current_user
)
from server.app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentResponse, PaymentResponseExtended
)


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/add_payment", response_model=PaymentResponse)
@required_plans(["customer", "performer"])
@required_permissions(["create_payment", "read_own_payment_list", "read_own_payment_details"])
def add_payment_details(
        payment_data: PaymentCreate,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return PaymentController.create_payment(
            user["id"],
            str(payment_data.payment)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/list", response_model=Union[list[PaymentResponse], PaymentResponse])
@required_plans(["customer", "performer"])
@required_permissions(["read_own_payment_list"])
def get_payment_list(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return PaymentController.get_user_payments(user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/list/{payment_id}", response_model=PaymentResponse)
@required_plans(["customer", "performer"])
@required_permissions(["read_own_payment_list", "read_own_payment_details"])
def get_payment_details(
        payment_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        PaymentValidator(payment_id=payment_id) \
        .validate_payment_ownership(user["id"])

        return PaymentController.get_payment(payment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me/list/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
@required_plans(["customer", "performer"])
@required_permissions(["read_own_payment_details", "delete_own_payment"])
def delete_payment(
        payment_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        PaymentValidator(payment_id=payment_id) \
        .validate_payment_ownership(user["id"])

        PaymentController.delete_payment(payment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/list", response_model=Union[list[PaymentResponseExtended], PaymentResponseExtended])
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_payments"])
def get_all_payments(
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return PaymentController.get_all_users_payments()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}/list", response_model=Union[list[PaymentResponse], PaymentResponse])
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_payments", "read_user_payments"])
def get_user_payments(
        user_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return PaymentController.get_user_payments(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}/list/{payment_id}", response_model=PaymentResponseExtended)
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_payments", "read_user_payments", "read_user_payment_details"])
def get_user_payment_details(
        user_id: int,
        payment_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        return PaymentController.get_user_payment_details(user_id, payment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}/list/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
@required_plans(["admin"])
@required_permissions(["read_all_users_payments", "read_user_payments", "read_user_payment_details", "delete_user_payment"])
def delete_user_payment(
        user_id: int,
        payment_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    try:
        PaymentValidator(payment_id=payment_id) \
        .validate_payment_ownership(user_id)

        PaymentController.delete_payment(payment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
