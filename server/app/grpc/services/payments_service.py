from google.protobuf import empty_pb2

from server.app.grpc.generated.payments_pb2_grpc import PaymentsServiceServicer
from server.app.grpc.generated.payments_pb2 import (
    CreatePaymentRequest,
    PaymentRequest,
    UserRequest,
    UserPaymentRequest,
    PaymentResponse,
    PaymentDetailResponse,
    PaymentListResponse,
    PaymentListResponsePerUser
)
from server.app.database.database import PostgresDatabase


class PaymentsService(PaymentsServiceServicer):
    def CreatePayment(self, request: CreatePaymentRequest, context):
        return super().CreatePayment(request, context)
    
    def GetAllUserPayments(self, request: empty_pb2, context):
        
        return super().GetAllUserPayments(request, context)

    def GetPayment(self, request: PaymentRequest, context):
        return super().GetPayment(request, context)
    
    def DeletePayment(self, request: PaymentRequest, context):  
        return super().DeletePayment(request, context)
    
    def AdminGetAllUsersPayments(self, request: empty_pb2, context):
        return super().AdminGetAllUsersPayments(request, context)
    
    def AdminGetAllUserPayments(self, request: UserRequest, context):
        return super().AdminGetAllUserPayments(request, context)
    
    def AdminGetUserPayment(self, request: UserPaymentRequest, context):
        return super().AdminGetUserPayment(request, context)
    
    def AdminDeleteUserPayment(self, request: UserPaymentRequest, context):
        return super().AdminDeleteUserPayment(request, context)
