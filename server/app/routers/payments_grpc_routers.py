from typing import Any, Union

from fastapi import APIRouter, Depends
from google.protobuf import empty_pb2
import grpc

from server.app.utils.dependencies.dependencies import get_token
from server.app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentResponse, 
    PaymentResponseExtended
)
from server.app.utils.exceptions import GlobalException
from server.app.grpc.generated import (
    payments_pb2, 
    payments_pb2_grpc
)


router = APIRouter(prefix="/grpc/payments", tags=["grpc_payments"])


@router.get("/me/list", response_model=Union[list[PaymentResponse], PaymentResponse])
@GlobalException.catcher
async def get_payment_list(
        token: str = Depends(get_token)
):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = payments_pb2_grpc.PaymentsServiceStub(channel)
        
        metadata = grpc.aio.Metadata(
            ("authorization", f"Bearer {token}")
        )

        response = await stub.GetAllUserPayments(empty_pb2.Empty(), metadata=metadata)
    return [PaymentResponse(id=payment.id, payment=payment.payment) for payment in response.payments]
